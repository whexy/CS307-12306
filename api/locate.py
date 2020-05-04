from flask import request, jsonify
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from sqlalchemy import or_
from sqlalchemy.orm import aliased

from model.Database import DBSession
from model.models import Province, District, City, Station, Train, Interval


class GeoApi(Resource):
    @jwt_required
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
    @jwt_required
    def get(self):
        train_name = request.args.get('train_name')
        session = DBSession()
        train_id = session.query(Train.train_id).filter(Train.train_name == train_name).first()
        interval_list = session.query(Interval.interval_id, City.city_name, District.district_name,
                                      Station.station_name, Interval.dep_datetime) \
            .join(Station, Station.station_id == Interval.dep_station) \
            .join(District, Station.district_id == District.district_id) \
            .join(City, District.city_id == City.city_id) \
            .filter(Interval.train_id == train_id) \
            .order_by(Interval.interval_id) \
            .all()

        resp = []
        id_num = 1
        for interval_id, city_name, district_name, station_name, dep_datetime in interval_list:
            resp.append({
                'id': id_num,
                'district': city_name + ',' + district_name,
                'station': station_name,
                'time': str(dep_datetime)
            })
            id_num += 1
        arv_datetime, last_city_name, last_district_name, last_station_name = \
            session.query(Interval.arv_datetime, City.city_name, District.district_name, Station.station_name) \
                .join(Station, Station.station_id == Interval.arv_station) \
                .join(District, Station.district_id == District.district_id) \
                .join(City, District.city_id == City.city_id) \
                .filter(Interval.interval_id == interval_list[-1][0]) \
                .first()
        resp.append({
            'id': id_num,
            'district': last_city_name + ',' + last_district_name,
            'station': last_station_name,
            'time': str(arv_datetime)
        })
        return jsonify(result=resp, code=0)


class TrainApiV2(Resource):
    @jwt_required
    def get(self):
        train_name = request.args.get('train_name')
        session = DBSession()
        first_id = session.query(Interval.interval_id) \
            .join(Train, Train.train_id == Interval.train_id) \
            .filter(Train.train_name == train_name, Interval.prev_id == None) \
            .first()

        successive_train = session.query(Interval.interval_id, Interval.dep_station, Interval.dep_datetime,
                                         Interval.next_id) \
            .filter(Interval.interval_id == first_id) \
            .cte(name='successive_train', recursive=True)
        st_alias = aliased(successive_train, name='st')
        i_alias = aliased(Interval, name='i')
        successive_train_rec = successive_train.union_all(
            session.query(i_alias.interval_id, i_alias.dep_station, i_alias.dep_datetime, i_alias.next_id)
                .filter(i_alias.interval_id == st_alias.c.next_id)
        )
        interval_list = session.query(successive_train_rec.c.interval_id, City.city_name, District.district_name,
                                      Station.station_name, successive_train_rec.c.dep_datetime) \
            .join(Station, Station.station_id == successive_train_rec.c.dep_station) \
            .join(District, Station.district_id == District.district_id) \
            .join(City, District.city_id == City.city_id) \
            .order_by(successive_train_rec.c.interval_id) \
            .all()

        resp = []
        id_num = 1
        for interval_id, city_name, district_name, station_name, dep_datetime in interval_list:
            resp.append({
                'id': id_num,
                'district': city_name + ',' + district_name,
                'station': station_name,
                'time': str(dep_datetime)
            })
            id_num += 1
        arv_datetime, last_city_name, last_district_name, last_station_name = \
            session.query(Interval.arv_datetime, City.city_name, District.district_name, Station.station_name) \
                .join(Station, Station.station_id == Interval.arv_station) \
                .join(District, Station.district_id == District.district_id) \
                .join(City, District.city_id == City.city_id) \
                .filter(Interval.interval_id == interval_list[-1][0]) \
                .first()
        resp.append({
            'id': id_num,
            'district': last_city_name + ',' + last_district_name,
            'station': last_station_name,
            'time': str(arv_datetime)
        })
        return jsonify(result=resp, code=0)
