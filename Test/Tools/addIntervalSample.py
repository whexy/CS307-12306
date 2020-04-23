import os
from datetime import time

from progressbar import Percentage, Bar, Timer, FileTransferSpeed, ETA, ProgressBar

from model.Database import DBSession
from model.models import Station, Train, Interval

session = DBSession()

errors = []
widgets = ['Progress: ', Percentage(), ' ', Bar('#'), ' ', Timer(),
           ' ', ETA(), ' ', FileTransferSpeed()]
for root, subFolders, files in os.walk('/Users/whexy/Downloads/12307_intervals'):
    pbar = ProgressBar(widgets=widgets, maxval=len(files)).start()
    for file_i, filename in enumerate(files):
        try:
            with open(os.path.join(root, filename)) as f:
                train_name = filename.split(".")[0]
                train: Train = session.query(Train).filter(Train.train_name == train_name).first()
                if train is not None:
                    # print("Skip " + train_name)
                    continue

                # print("Handling " + train_name)
                train = Train(train_name=train_name)
                session.add(train)
                session.commit()
                # print("Train {} not found, add to train table.".format(train_name))
                session.flush()

                intervals = f.read().splitlines()[::-1]  # 按照逆序读取
                interval_id_list = []  # 存储 id

                for interval in intervals:

                    interval_info = interval.split(',')

                    dep_s_name = ''.join(interval_info[1].split())
                    arv_s_name = ''.join(interval_info[3].split())

                    dep_s: Station = session.query(Station).filter(
                        Station.station_name == dep_s_name).first()
                    arv_s: Station = session.query(Station).filter(
                        Station.station_name == arv_s_name).first()

                    if dep_s is None:
                        with open("Station_Not_Found.txt", "a+") as f:
                            # print("Station {} not found".format(dep_s_name))
                            f.write(dep_s_name + "\n")
                        break

                    if arv_s is None:
                        with open("Station_Not_Found.txt", "a+") as f:
                            # print("Station {} not found".format(arv_s_name))
                            f.write(arv_s_name + "\n")
                        break

                    dep_t = time(int(interval_info[2][0:2]), int(interval_info[2][3:5]))
                    arv_t = time(int(interval_info[4][0:2]), int(interval_info[4][3:5]))

                    info = {
                        "train_id": train.train_id,
                        "dep_station": dep_s.station_id,
                        "arv_station": arv_s.station_id,
                        "dep_datetime": dep_t,
                        "arv_datetime": arv_t
                    }

                    new_interval = Interval(**info)
                    session.add(new_interval)
                    session.commit()
                    session.flush()
                    interval_id = new_interval.interval_id
                    interval_id_list.append(interval_id)

                for inv_i, interval_id in enumerate(interval_id_list):
                    interval = session.query(Interval).filter(Interval.interval_id == interval_id).first()
                    interval.next_id = interval_id_list[inv_i + 1] if inv_i < len(interval_id_list) - 1 else None
                    interval.prev_id = interval_id_list[inv_i - 1] if inv_i > 0 else None
                    session.commit()
                    session.flush()
        except:
            with open("error.txt", "a+") as f:
                f.write(filename + "\n")
            session = DBSession()
            continue
        finally:
            pbar.update(file_i)
    pbar.finish()
