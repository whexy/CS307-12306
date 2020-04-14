# coding: utf-8
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class City(Base):
    __tablename__ = 'city'

    city_id = Column(Integer, primary_key=True)
    city_name = Column(String(32), nullable=False, unique=True)


class Seat(Base):
    __tablename__ = 'seat'
    __table_args__ = (
        Index('seat_carriage_number_seat_number_uindex', 'carriage_number', 'seat_number', unique=True),
    )

    seat_id = Column(Integer, primary_key=True, unique=True, server_default=text("nextval('seat_seat_id_seq'::regclass)"))
    carriage_number = Column(Integer, nullable=False)
    seat_number = Column(String(10), nullable=False)
    seat_type = Column(String(10), nullable=False)
    is_available = Column(Boolean, nullable=False)


class Train(Base):
    __tablename__ = 'train'

    train_id = Column(Integer, primary_key=True)
    train_name = Column(String(15), nullable=False)


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True, unique=True, server_default=text("nextval('user_user_id_seq'::regclass)"))
    username = Column(String(255), nullable=False, unique=True)
    phone_number = Column(String(45), nullable=False)
    real_name = Column(String(45), nullable=False)
    email = Column(String(45), nullable=False)
    password = Column(String(45), nullable=False)


class Station(Base):
    __tablename__ = 'station'

    station_id = Column(Integer, primary_key=True)
    station_name = Column(String(32), nullable=False, unique=True)
    city_id = Column(ForeignKey('city.city_id'), nullable=False)

    city = relationship('City')


class Interval(Base):
    __tablename__ = 'interval'
    __table_args__ = (
        UniqueConstraint('train_id', 'dep_station', 'arv_station'),
    )

    interval_id = Column(Integer, primary_key=True)
    train_id = Column(ForeignKey('train.train_id'), nullable=False)
    dep_station = Column(ForeignKey('station.station_id'), nullable=False)
    arv_station = Column(ForeignKey('station.station_id'), nullable=False)
    dep_datetime = Column(DateTime, nullable=False)
    arv_datetime = Column(DateTime, nullable=False)
    prev_id = Column(Integer)
    next_id = Column(Integer)

    station = relationship('Station', primaryjoin='Interval.arv_station == Station.station_id')
    station1 = relationship('Station', primaryjoin='Interval.dep_station == Station.station_id')
    train = relationship('Train')


class Price(Base):
    __tablename__ = 'prices'
    __table_args__ = (
        UniqueConstraint('first_interval', 'last_interval', 'seat_type'),
    )

    price_id = Column(Integer, primary_key=True)
    first_interval = Column(ForeignKey('interval.interval_id'), nullable=False)
    last_interval = Column(ForeignKey('interval.interval_id'), nullable=False)
    seat_type = Column(Integer, nullable=False)
    price = Column(Float(53), nullable=False)

    interval = relationship('Interval', primaryjoin='Price.first_interval == Interval.interval_id')
    interval1 = relationship('Interval', primaryjoin='Price.last_interval == Interval.interval_id')


class Ticket(Base):
    __tablename__ = 'ticket'
    __table_args__ = (
        Index('ticket_first_interval_last_interval_seat_id_available_uindex', 'first_interval', 'last_interval', 'seat_id', 'available', unique=True),
    )

    ticket_id = Column(Integer, primary_key=True, unique=True, server_default=text("nextval('ticket_ticket_id_seq'::regclass)"))
    first_interval = Column(ForeignKey('interval.interval_id'), nullable=False)
    last_interval = Column(ForeignKey('interval.interval_id'), nullable=False)
    seat_id = Column(ForeignKey('seat.seat_id'), nullable=False)
    user_id = Column(ForeignKey('user.user_id'), nullable=False)
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

    order_id = Column(Integer, primary_key=True)
    order_timestamp = Column(DateTime, nullable=False)
    ticket_id = Column(ForeignKey('ticket.ticket_id'), nullable=False)
    order_status = Column(String(16), nullable=False)

    ticket = relationship('Ticket')
