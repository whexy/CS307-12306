from flask import request, jsonify
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from sqlalchemy import or_

from model.Database import DBSession
from model.models import Province, District, City, Station, Train, Interval


class AdminStationApi(Resource):
    """
    API class for station administration
    """
    @jwt_required
    def post(self):
        """
        Station addition API, **JWT required**

        **argument**:
         - `province_name`: `str`
         - `city_name`: `str`
         - `district_name`: `str`
         - `station_name`: `str`

        **return**: A JSON dictionary with values
         - `code`: `int`, equals to 0 if addition is successful
         - `result`: `str` for success message, shown if `code == 0`
         - `error`: `str`, shown if `code != 0`
        """
        session = DBSession()
        try:
            body = request.get_json()
            province_name = body.get('province_name')
            city_name = body.get('city_name')
            district_name = body.get('district_name')
            station_name = body.get('station_name')
            station = session.query(Station) \
                .join(District, Station.district_id == District.district_id) \
                .join(City, District.city_id == City.city_id) \
                .join(Province, Province.province_id == City.province_id) \
                .filter(Station.station_name == station_name,
                        District.district_name == district_name,
                        City.city_name == city_name,
                        Province.province_name == province_name) \
                .first()
            if station:
                if station.available:
                    return jsonify(code=1, error="站名已存在！")
                else:
                    station.available = True
                    session.commit()
                    return jsonify(code=0, result='添加成功')
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
        except:
            session.rollback()
            return jsonify(code=1, error='添加失败')
        finally:
            session.close()

    @jwt_required
    def patch(self):
        """
        Station modification API, **JWT required**

        **argument**:
         - `city_name`: `str`
         - `district_name`: `str`
         - `station_name`: `str`
         - `new_station_name`: `str`

        **return**: A JSON dictionary with values
         - `code`: `int`, equals to 0 if modification is successful
         - `result`: `str` for success message, shown if `code == 0`
         - `error`: `str`, shown if `code != 0`
        """
        session = DBSession()
        try:
            body = request.get_json()
            city_name = body.get('city_name')
            district_name = body.get('district_name')
            station_name = body.get('station_name')
            new_station_name = body.get('new_station_name')
            current_station: Station = session.query(Station).filter(Station.station_name == station_name,
                                                                     Station.available == True).first()
            if not current_station:
                return jsonify(code=1, error="站点不存在")

            district = session.query(District).filter(District.district_name == district_name).first()
            if not district:
                city = session.query(City).filter(City.city_name == city_name).first()
                new_district = District(district_name=district_name, city_id=city.city_id)
                session.add(new_district)
                session.commit()
                district = session.query(District).filter(District.district_name == district_name).first()
            current_station.district_id = district.district_id
            if new_station_name:
                current_station.station_name = new_station_name
            session.commit()
            return jsonify(code=0, result="修改成功")
        except:
            session.rollback()
            return jsonify(code=1, error='修改失败')
        finally:
            session.close()

    @jwt_required
    def delete(self):
        """
        Station deletion API, **JWT required**

        **argument**:
         - `station_name`: `str`

        **return**: A JSON dictionary with values
         - `code`: `int`, equals to 0 if deletion is successful
         - `result`: `str` for success message, shown if `code == 0`
         - `error`: `str`, shown if `code != 0`
        """
        session = DBSession()
        try:
            body = request.get_json()
            station_name = body.get('station_name')
            # Find if the station exists
            station: Station = session.query(Station).filter(Station.station_name == station_name,
                                                             Station.available == True).first()
            if not station:
                return jsonify(code=1, error="站点不存在或已删除")
            # Check if the station has train passing
            interval = session.query(Interval).filter(
                or_(Interval.dep_station == station.station_id, Interval.arv_station == station.station_id)).first()
            if interval:
                return jsonify(code=2, error="站点仍有火车经过")
            station.available = False
            session.commit()
            return jsonify(code=0, result="删除成功")
        finally:
            session.close()
