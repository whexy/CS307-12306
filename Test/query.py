import json
import urllib.parse

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from sqlalchemy import or_, func, BIGINT
from sqlalchemy.orm import aliased

from model.Database import DBSession
from model.Utils import get_nearby_station
from model.models import *


def get():
    dep_place = '%镇江%'
    arv_place = '%丹阳%'
    dg_only = True
    session = DBSession()
    station_table = session.query(Station.station_name, Station.station_id,
                                  District.district_name, City.city_name) \
        .join(District, Station.district_id == District.district_id) \
        .join(City, District.city_id == City.city_id)
    dep_station_table = station_table.filter(or_(District.district_name.like(dep_place),
                                                 Station.station_name.like(dep_place),
                                                 City.city_name.like(dep_place))) \
        .subquery()
    arv_station_table = station_table.filter(or_(District.district_name.like(arv_place),
                                                 Station.station_name.like(arv_place),
                                                 City.city_name.like(arv_place))) \
        .subquery()
    dep_train_info = session.query(Interval.train_id, Interval.dep_station) \
        .join(dep_station_table, Interval.dep_station == dep_station_table.c.station_id) \
        .subquery()
    arv_train_info = session.query(Interval.train_id, Interval.arv_station) \
        .join(arv_station_table, Interval.arv_station == arv_station_table.c.station_id) \
        .subquery()
    print('ding')
    raw_train_info = session.query(Interval.train_id, Train.train_name,
                                   func.min(Interval.interval_id).label('first_interval'),
                                   func.max(Interval.interval_id).label('last_interval')) \
        .join(Train, Train.train_id == Interval.train_id) \
        .join(dep_train_info, Interval.train_id == dep_train_info.c.train_id) \
        .join(arv_train_info, Interval.train_id == arv_train_info.c.train_id) \
        .filter(dep_train_info.c.dep_station != arv_train_info.c.arv_station,
                or_(Interval.dep_station == dep_train_info.c.dep_station,
                    Interval.arv_station == arv_train_info.c.arv_station)) \
        .group_by(Interval.train_id, Train.train_name) \
        .subquery()
    # raw_train_info = session.query(Interval.train_id, Train.train_name,
    #                                func.min(Interval.interval_id).label('first_interval'),
    #                                func.max(Interval.interval_id).label('last_interval')) \
    #     .join(Train, Train.train_id == Interval.train_id) \
    #     .filter(Interval.train_id.in_(dep_train_info.with_entities(Train.train_id).all()),
    #             Interval.train_id.in_(arv_train_info.with_entities(Train.train_id).all()),
    #             or_(Interval.dep_station.in_(dep_train_info.with_entities(Interval.dep_station).all()),
    #                 Interval.arv_station.in_(arv_train_info.with_entities(Interval.arv_station).all()))) \
    #     .group_by(Interval.train_id, Train.train_name) \
    #     .subquery()
    print('ding')
    dep_i = aliased(Interval, name='dep_i')
    arv_i = aliased(Interval, name='arv_i')
    dep_s = aliased(Station, name='dep_s')
    arv_s = aliased(Station, name='arv_s')
    train_info_list = session.query(raw_train_info.c.train_name,
                                    raw_train_info.c.first_interval, raw_train_info.c.last_interval,
                                    dep_s.station_name, func.cast(dep_i.dep_datetime, String),
                                    arv_s.station_name, func.cast(arv_i.arv_datetime, String)) \
        .join(dep_i, dep_i.interval_id == raw_train_info.c.first_interval) \
        .join(arv_i, arv_i.interval_id == raw_train_info.c.last_interval) \
        .join(dep_s, dep_s.station_id == dep_i.dep_station) \
        .join(arv_s, arv_s.station_id == arv_i.arv_station) \
        .order_by(dep_i.dep_datetime) \
        .all()
    train_info_list = list(filter(lambda x: x['train_name'][0] in 'DG' if dg_only else True,
                                  map(lambda x: dict(zip(
                                      ['train_name', 'first_interval', 'last_interval', 'dep_station',
                                       'dep_time', 'arv_station', 'arv_time'], x)), train_info_list)))
    return train_info_list


def test():
    session = DBSession()
    try:
        dep_place = '%南京%'
        arv_place = '%西安%'
        dg_only = True
        dep_train_info = session.query(Interval.train_id, Interval.dep_station) \
            .join(Station, Interval.dep_station == Station.station_id) \
            .filter(Station.station_name.like(dep_place)) \
            .subquery()
        arv_train_info = session.query(Interval.train_id, Interval.arv_station) \
            .join(Station, Interval.arv_station == Station.station_id) \
            .filter(Station.station_name.like(arv_place)) \
            .subquery()
        raw_train_info = session.query(Interval.train_id, Train.train_name,
                                       func.min(Interval.interval_id).label('first_interval'),
                                       func.max(Interval.interval_id).label('last_interval')) \
            .join(Train, Train.train_id == Interval.train_id) \
            .join(dep_train_info, Interval.train_id == dep_train_info.c.train_id) \
            .join(arv_train_info, Interval.train_id == arv_train_info.c.train_id) \
            .filter(or_(Interval.dep_station == dep_train_info.c.dep_station,
                        Interval.arv_station == arv_train_info.c.arv_station)) \
            .group_by(Interval.train_id, Train.train_name) \
            .subquery()
        dep_i = aliased(Interval, name='dep_i')
        arv_i = aliased(Interval, name='arv_i')
        dep_s = aliased(Station, name='dep_s')
        arv_s = aliased(Station, name='arv_s')
        train_info_list = session.query(raw_train_info.c.train_name,
                                        raw_train_info.c.first_interval, raw_train_info.c.last_interval,
                                        dep_s.station_name.label('dep_station'),
                                        func.cast(dep_i.dep_datetime, String).label('dep_time'),
                                        arv_s.station_name.label('arv_station'),
                                        func.cast(arv_i.arv_datetime, String).label('arv_time')) \
            .join(dep_i, dep_i.interval_id == raw_train_info.c.first_interval) \
            .join(arv_i, arv_i.interval_id == raw_train_info.c.last_interval) \
            .join(dep_s, dep_s.station_id == dep_i.dep_station) \
            .join(arv_s, arv_s.station_id == arv_i.arv_station) \
            .filter(dep_s.station_name.like(dep_place), arv_s.station_name.like(arv_place)) \
            .order_by(dep_i.dep_datetime) \
            .all()
        train_info_list = list(filter(lambda x: x['train_name'][0] in 'DG' if dg_only else True,
                                      map(lambda x: dict(zip(x.keys(), x)), train_info_list)))
        return dict(result=train_info_list, code=0)
    finally:
        session.close()


if __name__ == '__main__':
    print(json.dumps(test(), indent=4, ensure_ascii=False))
