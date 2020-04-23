from model.Database import DBSession
from model.models import *

session = DBSession()


def add_seats():
    with open('../Resources/cs307_public_interval.csv', 'r') as f:
        interval_list = f.read().splitlines()
    # interval_list = session.query(Interval.interval_id)
    for interval in interval_list:
        seat_type_list = list(map(lambda x: x[0],
                                  session.query(Price.seat_type_id)
                                  .filter(Price.interval_id == interval)
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
                                             is_available=True,
                                             interval_id=interval))
                    carriage_number += 1
            elif s == 2:
                for _ in range(2):
                    for i in range(1, 11):
                        for j in "ACDF":
                            session.add(Seat(carriage_number=carriage_number,
                                             seat_number=str(i) + j,
                                             seat_type_id=s,
                                             is_available=True,
                                             interval_id=interval))
                    carriage_number += 1
            elif s == 3:
                for _ in range(4):
                    for i in range(1, 17):
                        seat_type_id = 3
                        for j in "上中下":
                            session.add(Seat(carriage_number=carriage_number,
                                             seat_number='{}排{}铺'.format(i, j),
                                             seat_type_id=seat_type_id,
                                             is_available=True,
                                             interval_id=interval))
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
                                             is_available=True,
                                             interval_id=interval))
                            seat_type_id += 1
                    carriage_number += 1
        session.commit()
        print(interval, 'done')


if __name__ == '__main__':
    add_seats()
