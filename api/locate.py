from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import or_

from model.Database import DBSession
from model.models import Province, District, City, Station, Train, Interval


class GeoApi(Resource):
    def get(self):
        geo_name = request.args.get('geo_name')
        session = DBSession()
        stations = session.query(Province.province_name, City.city_name, District.district_name, Station.station_name) \
            .join(District, Station.district_id == District.district_id) \
            .join(City, District.city_id == City.city_id) \
            .join(Province, Province.province_id == City.province_id) \
            .filter(or_(District.district_name.like("%" + geo_name + "%"),
                        City.city_name.like("%" + geo_name + "%"),
                        Province.province_name.like("%" + geo_name + "%"))).all()
        resp = []
        for station in stations:
            resp.append(
                dict(province=station[0],
                     city=station[1],
                     district=station[2],
                     station=station[3]))
        return jsonify(result=resp, code=0)


class TrainApi(Resource):
    def get(self):
        train_name = request.args.get('train_name')
        session = DBSession()
        train_id = session.query(Train.train_id).filter(Train.train_name == train_name).first()
        city_name, district_name, station_name, next_id, dep_datetime = \
            session.query(City.city_name, District.district_name, Station.station_name, Interval.next_id,
                          Interval.dep_datetime) \
                .join(Interval, Interval.dep_station == Station.station_id) \
                .join(District, Station.district_id == District.district_id) \
                .join(City, District.city_id == City.city_id) \
                .filter(Interval.train_id == train_id, Interval.prev_id == None).first()

        resp = []
        id_num = 1
        resp.append(dict(id=1, district=city_name + ',' + district_name, station=station_name, time=str(dep_datetime)))
        while next_id:
            id_num += 1
            city_name, district_name, station_name, next_id, dep_datetime = \
                session.query(City.city_name, District.district_name, Station.station_name, Interval.next_id,
                              Interval.dep_datetime) \
                    .join(Interval, Interval.dep_station == Station.station_id) \
                    .join(District, Station.district_id == District.district_id) \
                    .join(City, District.city_id == City.city_id) \
                    .filter(Interval.interval_id == next_id).first()
            resp.append(dict(id=id_num, district=city_name + ',' + district_name, station=station_name,
                             time=str(dep_datetime)))
            if not next_id:
                city_name, district_name, station_name, dep_datetime = \
                    session.query(City.city_name, District.district_name, Station.station_name, Interval.arv_datetime) \
                        .join(Interval, Interval.arv_station == Station.station_id) \
                        .join(District, Station.district_id == District.district_id) \
                        .join(City, District.city_id == City.city_id) \
                        .filter(Interval.train_id == train_id, Interval.next_id == None).first()
                id_num += 1
                resp.append(dict(id=id_num, district=city_name + ',' + district_name, station=station_name,
                                 time=str(dep_datetime)))

        return jsonify(result=resp, code=0)
