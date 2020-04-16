from sqlalchemy import or_

from model.models import Station, District, City, Province


def get_nearby_station(place, session):
    return session.query(Station) \
        .join(District, Station.district_id == District.district_id) \
        .join(City, District.city_id == City.city_id) \
        .join(Province, Province.province_id == City.province_id) \
        .filter(or_(District.district_name.like("%" + place + "%"),
                    City.city_name.like("%" + place + "%"),
                    Province.province_name.like("%" + place + "%")))
