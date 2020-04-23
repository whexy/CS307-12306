from model.Database import DBSession
from model.models import *

session = DBSession()

with open('../Resources/station_city.csv', "r") as f:
    content = f.read().splitlines()[1:]

for line in content:
    station_name, province_name, city_name, district_name = line.split(",")
    if city_name == "[]":
        city_name = province_name
    if district_name == "[]":
        district_name = city_name

    # is province in the table
    province = session.query(Province).filter(Province.province_name == province_name).first()
    if province is None:
        new_province = Province(province_name=province_name)
        session.add(new_province)
        session.commit()
        province = session.query(Province).filter(Province.province_name == province_name).first()

    # is city in the table
    city = session.query(City).filter(City.city_name == city_name).first()
    if city is None:
        new_city = City(city_name=city_name, province_id=province.province_id)
        session.add(new_city)
        session.commit()
        city = session.query(City).filter(City.city_name == city_name).first()

    # is district in the table
    district = session.query(District).filter(District.district_name == district_name).first()
    if district is None:
        new_district = District(district_name=district_name, city_id=city.city_id)
        session.add(new_district)
        session.commit()
        district = session.query(District).filter(District.district_name == district_name).first()

    # add the station
    station = Station(station_name=station_name, district_id=district.district_id)
    session.add(station)
    session.commit()
