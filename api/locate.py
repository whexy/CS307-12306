from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy import or_

from model.Database import DBSession
from model.models import Province, District, City, Station


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
