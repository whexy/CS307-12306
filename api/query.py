import urllib.parse

from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import or_

from model.Database import DBSession
from model.Utils import get_nearby_station
from model.models import Interval, Train, Station, District, City


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
        depart_place = '%' + urllib.parse.unquote(request.args.get('from')) + '%'
        arrival_place = '%' + urllib.parse.unquote(request.args.get('to')) + '%'
        print(depart_place, arrival_place)
        session = DBSession()
        station_table = session.query(Station.station_name, Station.station_id,
                                      District.district_name, City.city_name) \
            .join(District, Station.district_id == District.district_id) \
            .join(City, District.city_id == City.city_id)
        depart_train_id = session.query(Interval.train_id) \
            .filter(Interval.dep_station.in_(station_table.filter(or_(Station.station_name.like(depart_place),
                                                                      District.district_name.like(depart_place),
                                                                      City.city_name.like(depart_place))
                                                                  )
                                             .with_entities(Station.station_id)))
        arrival_train_id = session.query(Interval.train_id) \
            .filter(Interval.arv_station.in_(station_table.filter(or_(Station.station_name.like(arrival_place),
                                                                      District.district_name.like(arrival_place),
                                                                      City.city_name.like(arrival_place))
                                                                  )
                                             .with_entities(Station.station_id)))
        train_info = session.query(Interval.train_id, Train.train_name) \
            .join(Train, Train.train_id == Interval.train_id) \
            .filter(Interval.train_id.in_(depart_train_id),
                    Interval.train_id.in_(arrival_train_id)) \
            .distinct()
        train_info_list = [{'train_id': info.train_id, "train_name": info.train_name} for info in train_info]
        return jsonify(result=train_info_list)
