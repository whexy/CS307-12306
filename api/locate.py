from flask import request, jsonify
from flask_restful import Resource

from model.Database import DBSession
from model.Utils import get_nearby_station


class GeoApi(Resource):
    def get(self):
        geo_name = request.args.get('geo_name')
        session = DBSession()
        stations = get_nearby_station(geo_name, session)
        resp = []
        for station in stations:
            resp.append(dict(station_id=station.station_id, station_name=station.station_name))
        return jsonify(result=resp, code=0)
