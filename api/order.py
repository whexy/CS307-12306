from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from sqlalchemy import BIGINT, func

from model.Database import DBSession
from model.Utils import get_interval_list
from model.models import *


class OrderApi(Resource):
    """
    API class for ticket ordering
    """
    @jwt_required
    def post(self):
        """
        Train order API, **JWT required**

        **return**: A JSON dictionary with values:
         - `code`: `int`, equals to 0 if order is successful
         - `result`: `dict` with values, shown if `code == 0`:
          - `order_id`: `int`
         - `error`: `str`, shown if `code != 0`
        """
        session = DBSession()
        try:
            user_id = get_jwt_identity()
            body = request.get_json()
            first_interval = int(body.get('first_interval'))
            last_interval = int(body.get('last_interval'))
            seat_class = body.get('seat_class')
            train_name = body.get('train_name')
            # successive_train_rec = get_interval_list(train_name, session)
            interval_list = get_interval_list(train_name, session)
            # interval_list = session.query(successive_train_rec.c.interval_id) \
            #     .order_by(successive_train_rec.c.interval_id) \
            #     .all()
            first_index = session.query(interval_list.c.interval_no) \
                .filter(interval_list.c.interval_id == first_interval) \
                .first() \
                .interval_no
            last_index = session.query(interval_list.c.interval_no) \
                .filter(interval_list.c.interval_id == last_interval) \
                .first() \
                .interval_no
            seat = session.query(Seat) \
                .join(Train, Train.train_id == Seat.train_id) \
                .filter(Train.train_name == train_name,
                        Seat.seat_type_id == seat_class,
                        func.cast(func.substring(Seat.occupied, first_index, last_index - first_index + 1),
                                  BIGINT) == 0) \
                .first()
            if seat is None:
                return jsonify(code=404, error='当前区间无余票！')
            seat.occupied = bin(
                int(seat.occupied, 2) | int('1' * (last_index - first_index + 1), 2) << (40 - last_index))[2:].zfill(40)
            new_ticket = Ticket(first_interval=first_interval, last_interval=last_interval, seat_id=seat.seat_id,
                                available=False)
            session.add(new_ticket)
            session.commit()
            session.flush()
            price = session.query(func.sum(Price.price).label('price')) \
                .join(interval_list, Price.interval_id == interval_list.c.interval_id) \
                .filter(Price.seat_type_id == seat_class, interval_list.c.interval_no <= last_index,
                        interval_list.c.interval_no >= first_index) \
                .first()
            new_order = Order(order_status='unpaid', user_id=user_id, ticket_id=new_ticket.ticket_id, price=price)
            session.add(new_order)
            session.commit()
            session.flush()
            return jsonify(code=0, result={'order_id': new_order.order_id})
        except:
            session.rollback()
            return jsonify(code=10, error='订票失败')
        finally:
            session.close()

    @jwt_required
    def delete(self):
        """
        Ticket refund API, **JWT required**

        **return**: A JSON dictionary with values:
         - `code`: `int`, equals to 0 if deletion is successful
         - `result`: `str`, shown if `code == 0`
         - `error`: `str`, shown if `code != 0`
        """
        session = DBSession()
        try:
            user_id = get_jwt_identity()
            body = request.get_json()
            order_id = body.get('order_id')
            # The delete function is to set the order status "cancelled", set ticket available false,
            # and released the occupied seat.
            current_order: Order = session.query(Order).filter(Order.order_id == order_id).first()
            # print(current_order.user_id, user_id)
            if int(user_id) != int(current_order.user_id):
                return jsonify(code=100, error='非法退票操作！')
            current_order.order_status = "cancelled"
            session.commit()
            session.flush()
            current_ticket: Ticket = session.query(Ticket).filter(Ticket.ticket_id == current_order.ticket_id).first()
            current_ticket.available = False
            session.commit()
            session.flush()
            first_interval = current_ticket.first_interval
            last_interval = current_ticket.last_interval
            current_seat: Seat = session.query(Seat).filter(Seat.seat_id == current_ticket.seat_id).first()
            train_id = session.query(Train.train_id).join(Interval, Interval.train_id == Train.train_id).filter(
                Interval.interval_id == first_interval, Interval.available == True, Train.available == True).first()

            # Here to release the seat
            train_name = session.query(Train.train_name).filter(Train.train_id == train_id,
                                                                Train.available == True).first().train_name
            interval_list = get_interval_list(train_name, session)
            # successive_train_rec = get_interval_list(train_name, session)
            # interval_list = session.query(successive_train_rec.c.interval_id) \
            #     .order_by(successive_train_rec.c.interval_id) \
            #     .all()
            first_index = session.query(interval_list.c.interval_no) \
                .filter(interval_list.c.interval_id == first_interval) \
                .first() \
                .interval_no
            last_index = session.query(interval_list.c.interval_no) \
                .filter(interval_list.c.interval_id == last_interval) \
                .first() \
                .interval_no
            current_seat.occupied = bin(
                int(current_seat.occupied, 2) & int('0' * (last_index - first_index + 1), 2) << (40 - last_index))[
                                    2:].zfill(40)
            session.commit()
            session.flush()
            return jsonify(code=0, result="操作成功，票已失效")
        except:
            session.rollback()
            return jsonify(code=10, error='操作失败，请联系管理员')
        finally:
            session.close()
