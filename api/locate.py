from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import or_, func, String, literal

from model.Database import DBSession
from model.Utils import get_interval_list
from model.models import Province, District, City, Station, Train, Interval


class GeoApi(Resource):
    def get(self):
        session = DBSession()
        try:
            geo_name = request.args.get('geo_name')
            stations = session.query(Province.province_name, City.city_name, District.district_name,
                                     Station.station_name) \
                .join(District, Station.district_id == District.district_id) \
                .join(City, District.city_id == City.city_id) \
                .join(Province, Province.province_id == City.province_id) \
                .filter(or_(Station.station_name.like('%' + geo_name + '%'),
                            District.district_name.like('%' + geo_name + '%'),
                            City.city_name.like('%' + geo_name + '%'),
                            Province.province_name.like('%' + geo_name + '%'))) \
                .all()
            resp = []
            for station in stations:
                resp.append(
                    dict(province=station[0],
                         city=station[1],
                         district=station[2],
                         station=station[3]))
            return jsonify(result=resp, code=0)
        finally:
            session.close()


class TrainApi(Resource):
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
    def get(self):
        session = DBSession()
        try:
            train_name = request.args.get('train_name')
            successive_train_rec = get_interval_list(train_name, session)
            interval_list = session.query(successive_train_rec.c.interval_no.label('id'),
                                          City.city_name.concat(',').concat(District.district_name).label('district'),
                                          Station.station_name.label('station'),
                                          func.cast(successive_train_rec.c.dep_datetime, String).label('time')) \
                .join(Station, Station.station_id == successive_train_rec.c.dep_station) \
                .join(District, Station.district_id == District.district_id) \
                .join(City, District.city_id == City.city_id) \
                .order_by(successive_train_rec.c.interval_id) \
                .all()

            last_no = interval_list[-1].id
            resp = list(map(lambda x: dict(zip(x.keys(), x)), interval_list))
            last_station = session.query(func.cast(successive_train_rec.c.arv_datetime, String).label('time'),
                                         City.city_name.concat(',').concat(District.district_name).label('district'),
                                         Station.station_name.label('station'),
                                         literal(last_no + 1).label('id')) \
                .join(Station, Station.station_id == successive_train_rec.c.arv_station) \
                .join(District, Station.district_id == District.district_id) \
                .join(City, District.city_id == City.city_id) \
                .filter(successive_train_rec.c.interval_no == last_no) \
                .first()
            resp.append(dict(zip(last_station.keys(), last_station)))
            return jsonify(result=resp, code=0)
        finally:
            session.close()


class AreaApi(Resource):
    def get(self):
        # return the list of provinces
        session = DBSession()
        try:
            province_name = request.args.get('province')
            city_name = request.args.get('city')
            if not province_name:
                province_list = session.query(Province.province_name).all()
                return jsonify(code=0, result=list(map(lambda x: dict(zip(x.keys(), x)), province_list)))
            elif not city_name:
                city_list = session.query(City.city_name).join(Province, Province.province_id == City.province_id) \
                    .filter(Province.province_name == province_name).all()
                return jsonify(code=0, result=list(map(lambda x: dict(zip(x.keys(), x)), city_list)))
            else:
                district_list = session.query(District.district_name) \
                    .join(City, City.city_id == District.city_id) \
                    .join(Province, Province.province_id == City.province_id) \
                    .filter(Province.province_name == province_name, City.city_name == city_name).all()
                return jsonify(code=0, result=list(map(lambda x: dict(zip(x.keys(), x)), district_list)))
        finally:
            session.close()
