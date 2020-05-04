from sqlalchemy import func

from model.Database import DBSession
from model.Utils import get_nearby_station
from model.models import Interval


def get():
    from_city = '镇江'
    to_city = '丹阳'
    dg_only = True
    session = DBSession()
    dep_stations = get_nearby_station(from_city, session)
    dep_intervals = session.query(Interval).filter(Interval.dep_station.in_(dep_stations))
    arv_stations = get_nearby_station(to_city, session)
    arv_intervals = session.query(Interval).filter(Interval.arv_station.in_(arv_stations))
    intervals = dep_intervals.union(arv_intervals).cte("intervals")
    nums = func.count('*').label('c')


if __name__ == '__main__':
    get()
