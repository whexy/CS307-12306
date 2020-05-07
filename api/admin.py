from flask import request, jsonify
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from sqlalchemy import or_, func, String, literal

from model.Database import DBSession
from model.Utils import get_interval_list
from model.models import Province, District, City, Station, Train, Interval


class AdminStationApi(Resource):
    @jwt_required
    def post(self):
        # New station
        session = DBSession()
        try:
            body = request.get_json()
            province_name = body.get('province_name')
            city_name = body.get('city_name')
            district_name = body.get('district_name')
            station_name = body.get('station_name')
            if session.query(Station).filter(Station.station_name == station_name).first():
                return jsonify(code=1, error="站名已存在！")
            province = session.query(Province).filter(Province.province_name == province_name).first()
            if province is None:
                new_province = Province(province_name=province_name)
                session.add(new_province)
                session.commit()
                province = session.query(Province).filter(Province.province_name == province_name).first()
            city = session.query(City).filter(City.city_name == city_name).first()
            if city is None:
                new_city = City(city_name=city_name, province_id=province.province_id)
                session.add(new_city)
                session.commit()
                city = session.query(City).filter(City.city_name == city_name).first()
            district = session.query(District).filter(District.district_name == district_name).first()
            if district is None:
                new_district = District(district_name=district_name, city_id=city.city_id)
                session.add(new_district)
                session.commit()
                district = session.query(District).filter(District.district_name == district_name).first()
            station = Station(station_name=station_name, district_id=district.district_id)
            session.add(station)
            session.commit()
            return jsonify(code=0, result="添加成功")
        finally:
            session.close()

    @jwt_required
    def patch(self):
        session = DBSession()
        try:
            body = request.get_json()
            city_name = body.get('city_name')
            district_name = body.get('district_name')
            station_name = body.get('station_name')
            current_station: Station = session.query(Station).filter(Station.station_name == station_name).first()
            if current_station is None:
                return jsonify(code=1, error="站点不存在")

            district = session.query(District).filter(District.district_name == district_name).first()
            if district is None:
                city = session.query(City).filter(City.city_name == city_name).first()
                new_district = District(district_name=district_name, city_id=city.city_id)
                session.add(new_district)
                session.commit()
                district = session.query(District).filter(District.district_name == district_name).first()
            current_station.district_id = district.district_id
            session.commit()
            return jsonify(code=0, result="添加成功")
        finally:
            session.close()

    @jwt_required
    def delete(self):
        session = DBSession()
        try:
            body = request.get_json()
            station_name = body.get('station_name')
            # Find if the station exists
            station: Station = session.query(Station).filter(Station.station_name == station_name).first()
            if not station:
                return jsonify(code=1, error="站点不存在")
            # Check if the station has train passing
            interval = session.query(Interval).filter(
                or_(Interval.dep_station == station.station_id, Interval.arv_station == station.station_id)).first()
            if interval:
                return jsonify(code=2, error="站点仍有火车经过")
            session.delete(station)
            session.commit()
            return jsonify(code=0, result="删除成功")
        finally:
            session.close()
