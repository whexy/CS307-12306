import json
from operator import or_

from sqlalchemy import literal
from sqlalchemy.orm import aliased

from model.Database import DBSession
from model.models import *


def test():
    train_name = 'Test000'
    allow_unavailable = True
    session = DBSession()
    first_id = session.query(Interval.interval_id) \
        .join(Train, Train.train_id == Interval.train_id) \
        .filter(Train.train_name == train_name, Interval.prev_id == None,
                or_(literal(allow_unavailable), Interval.available == True)) \
        .first() \
        .interval_id
    cte = session.query(Interval.interval_id, Interval.dep_station, Interval.arv_station, Interval.next_id,
                        literal(1).label('interval_no')) \
        .filter(Interval.interval_id == first_id) \
        .cte(name='cte', recursive=True)
    cte_alias = aliased(cte, name='c')
    i_alias = aliased(Interval, name='i')
    cte = cte.union_all(
        session.query(i_alias.interval_id, i_alias.dep_station, i_alias.arv_station, i_alias.next_id,
                      cte_alias.c.interval_no + 1)
            .filter(i_alias.interval_id == cte_alias.c.next_id)
    )
    cte_table = cte.c
    dep_s = aliased(Station, name='dep_s')
    arv_s = aliased(Station, name='arv_s')
    interval_info_list = session.query(cte_table.interval_id, dep_s.station_name.label('dep_station'),
                                       arv_s.station_name.label('arv_station'), cte_table.interval_no) \
        .join(dep_s, dep_s.station_id == cte_table.dep_station) \
        .join(arv_s, arv_s.station_id == cte_table.arv_station) \
        .order_by(cte_table.interval_no) \
        .all()
    # print(json.dumps(list(map(
    #     lambda x: dict(interval_id=x.interval_id, dep_station=x.dep_station, arv_station=x.arv_station,
    #                    interval_no=x.interval_no), interval_info_list)), indent=4, ensure_ascii=False))
    print(json.dumps(list(map(lambda x: dict(zip(x.keys(), x)), interval_info_list)), indent=4, ensure_ascii=False))
    print(interval_info_list[0].keys())


if __name__ == '__main__':
    test()
