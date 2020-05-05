import urllib.parse

from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import or_, func, BIGINT
from sqlalchemy.orm import aliased

from model.Database import DBSession
from model.Utils import get_nearby_station, get_interval_list
from model.models import *


class QueryApi(Resource):
    def get(self):
        depart_place = request.args.get('from')
        arrival_place = request.args.get('to')
        session = DBSession()
        depart_stations = get_nearby_station(depart_place, session)
        arrival_stations = get_nearby_station(arrival_place, session)
        depart_stations_id = [station.station_id for station in depart_stations]
        arrival_stations_id = [station.station_id for station in arrival_stations]

        depart_train_id = set([train.train_id for train in
                               session.query(Interval).filter(Interval.dep_station.in_(depart_stations_id))])
        arrival_train_id = set([train.train_id for train in
                                session.query(Interval).filter(Interval.arv_station.in_(arrival_stations_id))])
        train_id = depart_train_id.intersection(arrival_train_id)
        trains = session.query(Train).filter(Train.train_id.in_(list(train_id)))
        resp = []
        for train in trains:
            resp.append(train.train_name)

        # DEBUG
        # print(depart_stations_id, arrival_stations_id)
        # print(depart_train_id, arrival_train_id)
        # print(train_id)

        return jsonify(result=resp)


class QueryApiV2(Resource):
    def get(self):
        depart_place = request.args.get('from')
        arrival_place = request.args.get('to')
        SQL = '''
        with station_table as
         (
             select station_name, district_name, city_name, station_id
             from station
                      join district on station.district_id = district.district_id
                      join city on district.city_id = city.city_id
         )
select distinct i.train_id, train_name
from interval i
         join train on train.train_id = i.train_id
where i.train_id in
      (select train_id
       from interval
       where dep_station in (select station_id
                             from station_table
                             where station_name like '%{0}%'
                                or district_name like '%{0}%'
                                or city_name like '%{0}%'))
  and i.train_id in
      (select train_id
       from interval
       where arv_station in (select station_id
                             from station_table
                             where station_name like '%{1}%'
                                or district_name like '%{1}%'
                                or city_name like '%{1}%'))
        '''.format(depart_place, arrival_place)

        session = DBSession()
        resp = []
        sql_result = session.execute(SQL)
        for result in sql_result:
            resp.append({result[0]: result[1]})
        return jsonify(result=resp)


class QueryApiV3(Resource):
    def get(self):
        session = DBSession()
        try:
            dep_station = urllib.parse.unquote(request.args.get('dep_station'))
            arv_station = urllib.parse.unquote(request.args.get('arv_station'))
            dg_only = urllib.parse.unquote(request.args.get('DG_only')).lower() == 'true'
            dep_train_info = session.query(Interval.train_id, Interval.dep_station) \
                .join(Station, Interval.dep_station == Station.station_id) \
                .filter(Station.station_name == dep_station) \
                .subquery()
            arv_train_info = session.query(Interval.train_id, Interval.arv_station) \
                .join(Station, Interval.arv_station == Station.station_id) \
                .filter(Station.station_name == arv_station) \
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
                .filter(dep_s.station_name == dep_station, arv_s.station_name == arv_station) \
                .order_by(dep_i.dep_datetime) \
                .all()
            train_info_list = list(filter(lambda x: x['train_name'][0] in 'DG' if dg_only else True,
                                          map(lambda x: dict(zip(x.keys(), x)), train_info_list)))
            return jsonify(result=train_info_list, code=0)
        finally:
            session.close()


class QueryApiV4(Resource):
    def get(self):
        session = DBSession()
        try:
            dep_place = '%' + urllib.parse.unquote(request.args.get('dep_station')) + '%'
            arv_place = '%' + urllib.parse.unquote(request.args.get('arv_station')) + '%'
            dg_only = urllib.parse.unquote(request.args.get('DG_only')).lower() == 'true'
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


class TicketQuery(Resource):
    def get(self):
        session = DBSession()
        try:
            train_name = urllib.parse.unquote(request.args.get('train_name'))
            first_interval = int(urllib.parse.unquote(request.args.get('first_interval')))
            last_interval = int(urllib.parse.unquote(request.args.get('last_interval')))
            interval_list = get_interval_list(train_name, session)
            first_index = session.query(interval_list.c.interval_no) \
                .filter(interval_list.c.interval_id == first_interval) \
                .first() \
                .interval_no
            last_index = session.query(interval_list.c.interval_no) \
                .filter(interval_list.c.interval_id == last_interval) \
                .first() \
                .interval_no
            price_list = session.query(Price.seat_type_id, func.sum(Price.price).label('price')) \
                .join(interval_list, Price.interval_id == interval_list.c.interval_id) \
                .filter(interval_list.c.interval_no <= last_index, interval_list.c.interval_no >= first_index)  \
                .group_by(Price.seat_type_id) \
                .subquery()
            seats_left = session.query(Seat.seat_type_id, SeatType.name, func.count().label('left_cnt')) \
                .join(SeatType, SeatType.seat_type_id == Seat.seat_type_id) \
                .join(Train, Train.train_id == Seat.train_id) \
                .filter(Train.train_name == train_name,
                        func.cast(func.substring(Seat.occupied, first_index, last_index - first_index + 1),
                                  BIGINT) == 0) \
                .group_by(Seat.seat_type_id, SeatType.name) \
                .subquery()
            resp = session.query(seats_left.c.seat_type_id, seats_left.c.name.label('seat_type_name'),
                                 seats_left.c.left_cnt, price_list.c.price) \
                .join(price_list, price_list.c.seat_type_id == seats_left.c.seat_type_id) \
                .all()
            resp = list(sorted(map(lambda x: dict(zip(x.keys(), x)), resp), key=lambda x: x['seat_type_id']))
            return jsonify(result=resp, code=0)
        finally:
            session.close()
