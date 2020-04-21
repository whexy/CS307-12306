import os
from sys import stderr

from model.Database import DBSession
from model.models import *

session = DBSession()


def gao():
    global session
    for root, subFolders, files in os.walk('/Users/macmo/Downloads/12307_intervals'):
        for file in files:
            if file[0] == '.' or not file.endswith('.csv'):
                continue
            with open(os.path.join(root, file), 'r') as f:
                content = list(map(lambda x: x.split(','), f.read().splitlines()))
                for line in content:
                    train_name, dep, arv = line[:3]
                    result = session.query(Interval.interval_id, Train.train_name) \
                        .join(Station, Station.station_id == Interval.dep_station) \
                        .join(Train, Train.train_id == Interval.train_id) \
                        .filter(Train.train_name == train_name, Station.station_name == dep) \
                        .first()
                    if result is None:
                        print(train_name, 'not found')
                        with open('../../Resources/找不到的火车.txt', 'a+') as train_out:
                            train_out.write(','.join([train_name, dep, arv]) + '\n')
                        continue
                    interval_id, _ = result
                    # if interval_id is None:
                    #     print(train_name, dep, arv, 'not found')
                    #     with open('../../Resources/找不到的区间.txt', 'a+') as interval_out:
                    #         interval_out.write(','.join([train_name, dep, arv]) + '\n')
                    #     continue
                    seat_type_id = 1
                    for price in line[3:]:
                        if price != '-':
                            price_obj = Price(interval_id=interval_id, seat_type_id=seat_type_id, price=float(price))
                            session.add(price_obj)
                            try:
                                session.commit()
                            except:
                                print(interval_id, seat_type_id, price, 'insert error', file=stderr)
                                # session.rollback()
                                session = DBSession()
                        seat_type_id += 1
            print(file, 'done')


if __name__ == '__main__':
    gao()
