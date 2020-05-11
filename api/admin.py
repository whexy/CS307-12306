import traceback

from flask import request, jsonify
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from sqlalchemy import or_, func, String
from sqlalchemy.orm import aliased

from model.Database import DBSession
from model.Utils import get_interval_list
from model.models import Province, District, City, Station, Train, Interval, Price


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
                .filter(Station.station_name == station_name) \
                .first()
            exist_flag = False
            if station:
                if station.available:
                    return jsonify(code=1, error="站名已存在！")
                else:
                    district = session.query(District) \
                        .filter(District.district_id == station.district_id) \
                        .first()
                    if district.district_name == district_name:
                        station.available = True
                        session.commit()
                        return jsonify(code=0, result='站点{}添加成功'.format(station_name))
                    exist_flag = True
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
            if exist_flag:
                station.district_id = district.district_id
                station.available = True
            else:
                station = Station(station_name=station_name, district_id=district.district_id)
                session.add(station)
            session.commit()
            return jsonify(code=0, result='站点{}添加成功'.format(station_name))
        except:
            traceback.print_exc()
            session.rollback()
            return jsonify(code=1, error='添加失败，站点已存在或地址信息有误。')
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
        except:
            session.rollback()
            return jsonify(code=10, error='操作失败，请联系运维人员')
        finally:
            session.close()


class AdminTrainApi(Resource):
    """
    API class for train administration
    """

    @jwt_required
    def get(self):
        """
        Train information query API for administrator, **JWT required**

        **argument**:
         - `train_name`: `str`

        **return**: A JSON dictionary with values:
         - `code`: `int`, equals to 0 if query is successful
         - `error`: `str`, shown if `code != 0`
         - `result`: `list` of dictionaries of interval information:
          - `interval_id`: `int`
          - `interval_no`： `int`
          - `train_name`: `str`
          - `dep_station`: `str`
          - `arv_station`: `str`
          - `dep_datetime`: `str`
          - `arv_datetime`: `str`
          - `price`: `dict` containing:
           - `seat_type_1`, `str`
           - `seat_type_2`, `str`
           - `seat_type_3`, `str`
           - `seat_type_4`, `str`
           - `seat_type_5`, `str`
           - `seat_type_6`, `str`
           - `seat_type_7`, `str`
        """
        session = DBSession()
        try:
            train_name = request.args.get('train_name')
            interval_list = get_interval_list(train_name, session)
            dep_s = aliased(Station, name='dep_s')
            arv_s = aliased(Station, name='arv_s')
            res_list = session.query(interval_list.c.interval_id, interval_list.c.interval_no, Train.train_name,
                                     dep_s.station_name.label('dep_station'), arv_s.station_name.label('arv_station'),
                                     func.cast(interval_list.c.dep_datetime, String).label('dep_datetime'),
                                     func.cast(interval_list.c.arv_datetime, String).label('arv_datetime')) \
                .join(Train, Train.train_id == interval_list.c.train_id) \
                .join(dep_s, dep_s.station_id == interval_list.c.dep_station) \
                .join(arv_s, arv_s.station_id == interval_list.c.arv_station) \
                .order_by(interval_list.c.interval_no) \
                .all()
            res_list = list(map(lambda x: dict(zip(x.keys(), x)), res_list))
            for i in res_list:
                i['price'] = dict(zip(map(lambda x: 'seat_type_' + str(x), range(1, 8)), ['x'] * 7))
                price_list = session.query(Price).filter(Price.interval_id == i['interval_id']).all()
                i['price'].update(
                    dict(map(lambda x: ('seat_type_{}'.format(x.seat_type_id), '{:.2f}'.format(x.price)), price_list)))
            return jsonify(code=0, result=res_list)
        except:
            traceback.print_exc()
            return jsonify(code=10, error='Query error')
        finally:
            session.close()

    @jwt_required
    def post(self):
        """
        Train information update API for administrator, **JWT required**

        The body should be a JSON dictionary including the following attribute(s):
         - `interval_id`: `int`
         - `price`: `dict` containing:
          - `seat_type_1`, `str`
          - `seat_type_2`, `str`
          - `seat_type_3`, `str`
          - `seat_type_4`, `str`
          - `seat_type_5`, `str`
          - `seat_type_6`, `str`
          - `seat_type_7`, `str`


        **return**: A JSON dictionary with values:
         - `code`: `int`, equals to 0 if update is successful
         - `error`: `str`, shown if `code != 0`
         - `result`: `str`, shown if `code == 0`
        """
        session = DBSession()
        try:
            body = request.get_json()
            for raw_id, raw_price in body.get('price').items():
                seat_type_id = int(raw_id[-1])
                obj_price: Price = session.query(Price) \
                    .filter(Price.interval_id == body.get('interval_id'),
                            Price.seat_type_id == seat_type_id) \
                    .first()
                if obj_price:
                    price = float(raw_price)
                    if price > 0:
                        obj_price.price = price
                    else:
                        raise Exception('')
            session.commit()
            return jsonify(code=0, result='修改成功')
        except:
            session.rollback()
            return jsonify(code=10, error='修改失败')
        finally:
            session.close()
