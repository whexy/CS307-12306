from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import or_

from model.Database import DBSession
from model.models import City, District, Station, Province


class GeoApi(Resource):
    def get(self):
        geo_name = request.args.get('geo_name')
        session = DBSession()
        stations = session.query(Station) \
            .join(District, Station.district_id == District.district_id) \
            .join(City, District.city_id == City.city_id) \
            .join(Province, Province.province_id == City.province_id) \
            .filter(or_(
            District.district_name.like("%" + geo_name + "%"), City.city_name.like(
                "%" + geo_name + "%"), Province.province_name.like("%" + geo_name + "%")))
        resp = []
        for station in stations:
            resp.append(dict(station_id=station.station_id, station_name=station.station_name))
        return jsonify(result=resp)
