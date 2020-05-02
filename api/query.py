import urllib.parse

from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import or_, func
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
        dep_place = '%' + urllib.parse.unquote(request.args.get('from')) + '%'
        arv_place = '%' + urllib.parse.unquote(request.args.get('to')) + '%'
        DG_only = urllib.parse.unquote(request.args.get('DG_only'))
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
            .all()
        train_info_list = []
        for train_id, train_name, first_interval, last_interval in raw_train_info:
            first_id = session.query(Interval.interval_id) \
                .join(Train, Train.train_id == Interval.train_id) \
                .filter(Train.train_id == train_id, Interval.prev_id == None) \
                .first()[0]
            seats_left = session.query(Seat.seat_type, func.count().label('left_cnt')) \
                .filter(Seat.train_id == train_id,
                        func.substr(Seat.occupied, first_interval - first_id + 1,
                                    last_interval - first_interval + 1) == '0' * (last_interval - first_interval + 1)) \
                .group_by(Seat.seat_type) \
                .all()
            train_info_list.append({
                'train_name': train_name,
                'ticket_left': seats_left
            })
        return jsonify(result=train_info_list, code=0)
