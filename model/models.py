from flask_bcrypt import generate_password_hash, check_password_hash
from sqlalchemy import Column, ForeignKey, Integer, String, Time, UniqueConstraint, text, Float, Index, Boolean, \
    DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


class Province(Base):
    __tablename__ = 'province'

    province_id = Column(Integer, primary_key=True, unique=True,
                         server_default=text("nextval('province_province_id_seq'::regclass)"))
    province_name = Column(String(45), nullable=False, unique=True)


class Train(Base):
    __tablename__ = 'train'

    train_id = Column(Integer, primary_key=True, server_default=text("nextval('train_train_id_seq'::regclass)"))
    train_name = Column(String(15), nullable=False)


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, unique=True,
                     server_default=text("nextval('user_user_id_seq'::regclass)"))
    username = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String(45), nullable=False)
    real_name = Column(String(45), nullable=False)
    email = Column(String(45), nullable=False)
    password = Column(String(100), nullable=False)

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'username': self.username,
            'phone_number': self.phone_number,
            'real_name': self.real_name,
            'email': self.email,
        }


class City(Base):
    __tablename__ = 'city'

    city_id = Column(Integer, primary_key=True, server_default=text("nextval('city_city_id_seq'::regclass)"))
    city_name = Column(String(32), nullable=False, unique=True)
    province_id = Column(ForeignKey('province.province_id'), nullable=False)

    province = relationship('Province')


class District(Base):
    __tablename__ = 'district'

    district_id = Column(Integer, primary_key=True, unique=True,
                         server_default=text("nextval('district_district_id_seq'::regclass)"))
    district_name = Column(String(45), nullable=False)
    city_id = Column(ForeignKey('city.city_id'), nullable=False)

    city = relationship('City')


class Station(Base):
    __tablename__ = 'station'

    station_id = Column(Integer, primary_key=True, server_default=text("nextval('station_station_id_seq'::regclass)"))
    station_name = Column(String(32), nullable=False, unique=True)
    district_id = Column(ForeignKey('district.district_id'), nullable=False)

    district = relationship('District')


class Interval(Base):
    __tablename__ = 'interval'
    __table_args__ = (
        UniqueConstraint('train_id', 'dep_station', 'arv_station'),
    )

    interval_id = Column(Integer, primary_key=True,
                         server_default=text("nextval('interval_interval_id_seq'::regclass)"))
    train_id = Column(ForeignKey('train.train_id'), nullable=False)
    dep_station = Column(ForeignKey('station.station_id'), nullable=False)
    arv_station = Column(ForeignKey('station.station_id'), nullable=False)
    dep_datetime = Column(Time, nullable=False)
    arv_datetime = Column(Time, nullable=False)
    prev_id = Column(Integer)
    next_id = Column(Integer)

    station = relationship('Station', primaryjoin='Interval.arv_station == Station.station_id')
    station1 = relationship('Station', primaryjoin='Interval.dep_station == Station.station_id')
    train = relationship('Train')


class Price(Base):
    __tablename__ = 'prices'
    __table_args__ = (
        Index('prices_interval_id_seat_type_id_uindex', 'interval_id', 'seat_type_id', unique=True),
    )

    price_id = Column(Integer, primary_key=True, server_default=text("nextval('prices_price_id_seq'::regclass)"))
    interval_id = Column(ForeignKey('interval.interval_id'), nullable=False)
    seat_type_id = Column(ForeignKey('seat_type.seat_type_id'), nullable=False)
    price = Column(Float(53), nullable=False)

    interval = relationship('Interval')
    seat_type = relationship('SeatType')


class Seat(Base):
    __tablename__ = 'seat'
    __table_args__ = (
        Index('seat_carriage_number_seat_number_interval_id_uindex', 'carriage_number', 'seat_number', 'interval_id', unique=True),
    )

    seat_id = Column(Integer, primary_key=True, unique=True, server_default=text("nextval('seat_seat_id_seq'::regclass)"))
    carriage_number = Column(Integer, nullable=False)
    seat_number = Column(String(10), nullable=False)
    seat_type_id = Column(ForeignKey('seat_type.seat_type_id'), nullable=False)
    is_available = Column(Boolean, nullable=False)
    interval_id = Column(ForeignKey('interval.interval_id'), nullable=False)

    interval = relationship('Interval')
    seat_type = relationship('SeatType')


class Ticket(Base):
    __tablename__ = 'ticket'
    __table_args__ = (
        Index('ticket_first_interval_last_interval_seat_id_available_uindex', 'first_interval', 'last_interval',
              'seat_id', 'available', unique=True),
    )

    ticket_id = Column(Integer, primary_key=True, unique=True,
                       server_default=text("nextval('ticket_ticket_id_seq'::regclass)"))
    first_interval = Column(ForeignKey('interval.interval_id'), nullable=False)
    last_interval = Column(ForeignKey('interval.interval_id'), nullable=False)
    seat_id = Column(ForeignKey('seat.seat_id'), nullable=False)
    user_id = Column(ForeignKey('users.user_id'), nullable=False)
    available = Column(Boolean, nullable=False)

    interval = relationship('Interval', primaryjoin='Ticket.first_interval == Interval.interval_id')
    interval1 = relationship('Interval', primaryjoin='Ticket.last_interval == Interval.interval_id')
    seat = relationship('Seat')
    user = relationship('User')


class Order(Base):
    __tablename__ = 'orders'
    __table_args__ = (
        UniqueConstraint('order_timestamp', 'ticket_id', 'order_status'),
    )

    order_id = Column(Integer, primary_key=True, server_default=text("nextval('orders_order_id_seq'::regclass)"))
    order_timestamp = Column(DateTime, nullable=False)
    ticket_id = Column(ForeignKey('ticket.ticket_id'), nullable=False)
    order_status = Column(String(16), nullable=False)

    ticket = relationship('Ticket')


class SeatType(Base):
    __tablename__ = 'seat_type'

    seat_type_id = Column(Integer, primary_key=True, unique=True, server_default=text("nextval('table_name_seat_type_id_seq'::regclass)"))
    name = Column(String(16), nullable=False, unique=True)
