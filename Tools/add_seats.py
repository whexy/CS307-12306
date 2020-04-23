from model.Database import DBSession
from model.models import *

session = DBSession()


def add_seats():
    with open('../Resources/cs307_public_train.csv', 'r') as f:
        train_list = f.read().splitlines()
    # interval_list = session.query(Interval.interval_id)
    for train_id in train_list:
        interval_id = session.query(Interval.interval_id) \
            .filter(Interval.train_id == train_id) \
            .first()
        seat_type_list = list(map(lambda x: x[0],
                                  session.query(Price.seat_type_id)
                                  .filter(Price.interval_id == interval_id)
                                  .all()))
        carriage_number = 1
        for s in sorted(seat_type_list):
            if s == 1:
                for _ in range(4):
                    for i in range(1, 17):
                        for j in "ABCDF":
                            session.add(Seat(carriage_number=carriage_number,
                                             seat_number=str(i) + j,
                                             seat_type_id=s,
                                             occupied='0' * 100,
                                             train_id=train_id))
                    carriage_number += 1
            elif s == 2:
                for _ in range(2):
                    for i in range(1, 11):
                        for j in "ACDF":
                            session.add(Seat(carriage_number=carriage_number,
                                             seat_number=str(i) + j,
                                             seat_type_id=s,
                                             occupied='0' * 100,
                                             train_id=train_id))
                    carriage_number += 1
            elif s == 3:
                for _ in range(4):
                    for i in range(1, 17):
                        seat_type_id = 3
                        for j in "上中下":
                            session.add(Seat(carriage_number=carriage_number,
                                             seat_number='{}排{}铺'.format(i, j),
                                             seat_type_id=seat_type_id,
                                             occupied='0' * 100,
                                             train_id=train_id))
                            seat_type_id += 1
                    carriage_number += 1
            elif s == 6:
                for _ in range(2):
                    for i in range(1, 17):
                        seat_type_id = 6
                        for j in "上下":
                            session.add(Seat(carriage_number=carriage_number,
                                             seat_number='{}排{}铺'.format(i, j),
                                             seat_type_id=seat_type_id,
                                             occupied='0' * 100,
                                             train_id=train_id))
                            seat_type_id += 1
                    carriage_number += 1
        session.commit()
        print(train_id, 'done')


if __name__ == '__main__':
    add_seats()
