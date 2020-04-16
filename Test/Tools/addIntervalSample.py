import json
import os
from datetime import time

from model.Database import DBSession
from model.models import Station, Train, Interval

session = DBSession()

current_id = 0
errors = []

with open("todolist.txt", "r") as f:
    todo = f.read().splitlines()

for filename in todo:
    try:
        with open(os.path.join("/Users/whexy/Downloads/12306/new", filename)) as f:
            train_name = filename.split(".")[0]
            print(str(current_id) + ": Handling " + train_name)

            train: Train = session.query(Train).filter(Train.train_name == train_name).first()
            train_list = json.loads(f.read())
            interval_id_list = []
            for id, interval in enumerate(train_list[:-1]):
                # 处理字符空格的问题
                dep_s_name = ''.join(interval["SNAME"].split())
                arv_s_name = ''.join(train_list[id + 1]["SNAME"].split())

                dep_s: Station = session.query(Station).filter(
                    Station.station_name == dep_s_name).first()
                arv_s: Station = session.query(Station).filter(
                    Station.station_name == arv_s_name).first()

                if arv_s is None:
                    with open("Station_Not_Found.txt", "a+") as f:
                        f.write(arv_s_name + "\n")
                    break

                dep_t = time(int(interval["STIME"][0:2]), int(interval["STIME"][2:4]))
                arv_t = time(int(train_list[id + 1]["ATIME"][0:2]), int(train_list[id + 1]["ATIME"][2:4]))
                info = {
                    "train_id": train.train_id,
                    "dep_station": dep_s.station_id,
                    "arv_station": arv_s.station_id if arv_s is not None else None,
                    "dep_datetime": dep_t,
                    "arv_datetime": arv_t
                }
                new_interval = Interval(**info)
                session.add(new_interval)
                session.commit()
                session.flush()
                interval_id = new_interval.interval_id
                interval_id_list.append(interval_id)

            if arv_s is None:
                break

            for id, interval_id in enumerate(interval_id_list):
                interval = session.query(Interval).filter(Interval.interval_id == interval_id).first()
                interval.next_id = interval_id_list[id + 1] if id < len(interval_id_list) - 1 else None
                interval.prev_id = interval_id_list[id - 1] if id > 0 else None
                session.commit()
                session.flush()
    except:
        with open("error.txt", "a+") as f:
            f.write(filename + "\n")
        session = DBSession()
    current_id += 1
