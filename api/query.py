import urllib.parse

from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import or_, func, BIGINT
from sqlalchemy.orm import aliased

from model.Database import DBSession
from model.Utils import get_nearby_station
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
        dep_place = '%' + urllib.parse.unquote(request.args.get('from_city')) + '%'
        arv_place = '%' + urllib.parse.unquote(request.args.get('to_city')) + '%'
        dg_only = urllib.parse.unquote(request.args.get('DG_only')).lower() == 'true'
        session = DBSession()
        station_table = session.query(Station.station_name, Station.station_id,
                                      District.district_name, City.city_name) \
            .join(District, Station.district_id == District.district_id) \
            .join(City, District.city_id == City.city_id)
        dep_train_id = session.query(Interval.train_id) \
            .filter(Interval.dep_station.in_(station_table.filter(or_(Station.station_name.like(dep_place),
                                                                      District.district_name.like(dep_place),
                                                                      City.city_name.like(dep_place))
                                                                  )
                                             .with_entities(Station.station_id)))
        arv_train_id = session.query(Interval.train_id) \
            .filter(Interval.arv_station.in_(station_table.filter(or_(Station.station_name.like(arv_place),
                                                                      District.district_name.like(arv_place),
                                                                      City.city_name.like(arv_place))
                                                                  )
                                             .with_entities(Station.station_id)))
        raw_train_info = session.query(Interval.train_id, Train.train_name,
                                       func.min(Interval.interval_id).label('first_interval'),
                                       func.max(Interval.interval_id).label('last_interval')) \
            .join(Train, Train.train_id == Interval.train_id) \
            .filter(Interval.train_id.in_(dep_train_id), Interval.train_id.in_(arv_train_id)) \
            .group_by(Interval.train_id, Train.train_name) \
            .subquery()
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
        return jsonify(result=train_info_list, code=0)


class TicketQuery(Resource):
    def get(self):
        train_name = urllib.parse.unquote(request.args.get('train_name'))
        first_interval = int(urllib.parse.unquote(request.args.get('first_interval')))
        last_interval = int(urllib.parse.unquote(request.args.get('last_interval')))
        session = DBSession()
        first_id = session.query(Interval.interval_id) \
            .join(Train, Train.train_id == Interval.train_id) \
            .filter(Train.train_name == train_name, Interval.prev_id == None) \
            .first()[0]
        seats_left = session.query(Seat.seat_type_id, func.count().label('left_cnt')) \
            .join(Train, Train.train_id == Seat.train_id) \
            .filter(Train.train_name == train_name,
                    func.cast(func.substring(Seat.occupied, first_interval - first_id + 1,
                                             last_interval - first_interval + 1), BIGINT) == 0) \
            .group_by(Seat.seat_type_id) \
            .all()
        return jsonify(result=seats_left, code=0)
