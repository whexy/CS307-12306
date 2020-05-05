from sqlalchemy import or_, literal
from sqlalchemy.orm import aliased

from model.models import *


def get_nearby_station(place, session):
    return session.query(Station) \
        .join(District, Station.district_id == District.district_id) \
        .join(City, District.city_id == City.city_id) \
        .join(Province, Province.province_id == City.province_id) \
        .filter(or_(District.district_name.like("%" + place + "%"),
                    City.city_name.like("%" + place + "%"),
                    Province.province_name.like("%" + place + "%")))


def get_interval_list(train_name, session):
    first_id = session.query(Interval.interval_id) \
        .join(Train, Train.train_id == Interval.train_id) \
        .filter(Train.train_name == train_name, Interval.prev_id == None) \
        .first() \
        .interval_id
    cte = session.query(Interval, literal(1).label('interval_no')) \
        .filter(Interval.interval_id == first_id) \
        .cte(name='cte', recursive=True)
    cte_alias = aliased(cte, name='c')
    i_alias = aliased(Interval, name='i')
    cte = cte.union_all(
        session.query(i_alias, cte_alias.c.interval_no + 1)
            .filter(i_alias.interval_id == cte_alias.c.next_id)
    )
    return cte
