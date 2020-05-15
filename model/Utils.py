from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import or_, literal, func
from sqlalchemy.orm import aliased

from model.Database import DBSession
from model.models import *


def get_nearby_station(place, session):
    return session.query(Station) \
        .join(District, Station.district_id == District.district_id) \
        .join(City, District.city_id == City.city_id) \
        .join(Province, Province.province_id == City.province_id) \
        .filter(or_(District.district_name.like("%" + place + "%"),
                    City.city_name.like("%" + place + "%"),
                    Province.province_name.like("%" + place + "%")),
                Station.available == True)


def get_interval_list(train_name, session, allow_unavailable=False):
    first_id = session.query(Interval.interval_id) \
        .join(Train, Train.train_id == Interval.train_id) \
        .filter(Train.train_name == train_name, Interval.prev_id == None,
                or_(literal(allow_unavailable), Interval.available == True)) \
        .first() \
        .interval_id
    cte = session.query(Interval, literal(1).label('interval_no')) \
        .filter(Interval.interval_id == first_id, or_(literal(allow_unavailable), Interval.available == True)) \
        .cte(name='cte', recursive=True)
    cte_alias = aliased(cte, name='c')
    i_alias = aliased(Interval, name='i')
    cte = cte.union_all(
        session.query(i_alias, cte_alias.c.interval_no + 1)
            .filter(i_alias.interval_id == cte_alias.c.next_id,
                    or_(literal(allow_unavailable), i_alias.available == True))
    )
    return cte


def fuzzy_query(dep_place, arv_place, dg_only, session):
    dep_train_info = session.query(Interval.train_id, Interval.dep_station) \
        .join(Station, Interval.dep_station == Station.station_id) \
        .filter(Station.station_name.like(dep_place),
                Station.available == True,
                Interval.available == True) \
        .subquery()
    arv_train_info = session.query(Interval.train_id, Interval.arv_station) \
        .join(Station, Interval.arv_station == Station.station_id) \
        .filter(Station.station_name.like(arv_place),
                Station.available == True,
                Interval.available == True) \
        .subquery()
    raw_train_info = session.query(Interval.train_id, Train.train_name,
                                   func.min(Interval.interval_id).label('first_interval'),
                                   func.max(Interval.interval_id).label('last_interval')) \
        .join(Train, Train.train_id == Interval.train_id) \
        .join(dep_train_info, Interval.train_id == dep_train_info.c.train_id) \
        .join(arv_train_info, Interval.train_id == arv_train_info.c.train_id) \
        .filter(or_(Interval.dep_station == dep_train_info.c.dep_station,
                    Interval.arv_station == arv_train_info.c.arv_station),
                Train.available == True) \
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
        .filter(dep_s.station_name.like(dep_place), arv_s.station_name.like(arv_place),
                dep_s.available == True, arv_s.available == True,
                dep_i.available == True, arv_i.available == True) \
        .order_by(dep_i.dep_datetime) \
        .all()
    return list(filter(lambda x: x['train_name'][0] in 'DG' if dg_only else True,
                       map(lambda x: dict(zip(x.keys(), x)), train_info_list)))


def check_admin(fun):
    def wrapper(*args, **kwargs):
        session = DBSession()
        user_id = get_jwt_identity()
        is_admin = session.query(User.is_admin).filter(User.user_id == user_id).first()
        session.close()
        if is_admin[0]:
            return fun(*args, **kwargs)
        else:
            return jsonify(code=10, error='该用户没有管理员权限，无法执行管理员操作')
    return wrapper


def check_not_empty(*req_args):
    def decorator(fun):
        def wrapper(*args, **kwargs):
            for arg in req_args:
                if not request.args.get(arg):
                    return jsonify(code=21, error='请求内容不能为空')
            return fun(*args, **kwargs)
        return wrapper
    return decorator
