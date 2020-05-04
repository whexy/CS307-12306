from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from sqlalchemy import BIGINT, func
from sqlalchemy.orm import aliased

from model.Database import DBSession
from model.models import *


class OrderApi(Resource):
    @jwt_required
    def post(self):
        user_id = get_jwt_identity()
        body = request.get_json()
        session = DBSession()
        first_interval = int(body.get('first_interval'))
        last_interval = int(body.get('last_interval'))
        seat_class = body.get('seat_class')
        train_name = body.get('train_name')
        first_id = session.query(Interval.interval_id) \
            .join(Train, Train.train_id == Interval.train_id) \
            .filter(Train.train_name == train_name, Interval.prev_id == None) \
            .first()[0]
        successive_train = session.query(Interval.interval_id, Interval.next_id) \
            .filter(Interval.interval_id == first_id) \
            .cte(name='successive_train', recursive=True)
        st_alias = aliased(successive_train, name='st')
        i_alias = aliased(Interval, name='i')
        successive_train_rec = successive_train.union_all(
            session.query(i_alias.interval_id, i_alias.next_id)
                .filter(i_alias.interval_id == st_alias.c.next_id)
        )
        interval_list = session.query(successive_train_rec.c.interval_id) \
            .order_by(successive_train_rec.c.interval_id) \
            .all()
        index = 1
        first_index, last_index = 0, 0
        for interval in interval_list:
            interval_id = interval[0]
            if interval_id == first_interval:
                first_index = index
            if interval_id == last_interval:
                last_index = index
            index += 1
        seat = session.query(Seat) \
            .join(Train, Train.train_id == Seat.train_id) \
            .filter(Train.train_name == train_name,
                    Seat.seat_type_id == seat_class,
                    func.cast(func.substring(Seat.occupied, first_index, last_index - first_index + 1), BIGINT) == 0) \
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
        new_order = Order(order_status='unpaid', user_id=user_id, ticket_id=new_ticket.ticket_id)
        session.add(new_order)
        session.commit()
        session.flush()
        return jsonify(code=0, result={'order_id': new_order.order_id})

    def delete(self):
        body = request.get_json()
        order_id = body.get('order_id')
        # The delete function is to set the order status "cancelled", set ticket available false,
        # and released the occupied seat.
        session = DBSession()
        current_order: Order = session.query(Order).filter(Order.order_id == order_id).first()
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
            Interval.interval_id == first_interval).first()

        # Here to release the seat
        first_id = session.query(Interval.interval_id) \
            .join(Train, Train.train_id == Interval.train_id) \
            .filter(Train.train_id == train_id, Interval.prev_id == None) \
            .first()[0]
        successive_train = session.query(Interval.interval_id, Interval.next_id) \
            .filter(Interval.interval_id == first_id) \
            .cte(name='successive_train', recursive=True)
        st_alias = aliased(successive_train, name='st')
        i_alias = aliased(Interval, name='i')
        successive_train_rec = successive_train.union_all(
            session.query(i_alias.interval_id, i_alias.next_id)
                .filter(i_alias.interval_id == st_alias.c.next_id)
        )
        interval_list = session.query(successive_train_rec.c.interval_id) \
            .order_by(successive_train_rec.c.interval_id) \
            .all()
        index = 1
        first_index, last_index = 0, 0
        for interval in interval_list:
            interval_id = interval[0]
            if interval_id == first_interval:
                first_index = index
            if interval_id == last_interval:
                last_index = index
            index += 1
        current_seat.occupied = bin(
            int(current_seat.occupied, 2) & int('0' * (last_index - first_index + 1), 2) << (40 - last_index))[
                                2:].zfill(40)
        session.commit()
        session.flush()
        return dict(code=0, result="Delete Success")
