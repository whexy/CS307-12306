from flask import request, jsonify
from flask_restful import Resource

from model.Database import DBSession
from model.models import *


class PurchaseApi(Resource):
    def get(self):
        try:
            order_id = request.args.get('order_id')
            session = DBSession()
            current_order: Order = session.query(Order).filter(Order.order_id == order_id).first()
            current_order.order_status = "paid"
            session.commit()
            session.flush()
            current_ticket: Ticket = session.query(Ticket).filter(Ticket.ticket_id == current_order.ticket_id).first()
            current_ticket.available = True
            session.commit()
            session.flush()
            return "付款成功"
        except:
            return "付款失败"

    def post(self):
        body = request.get_json()
        order_id = body.get("order_id")
        session = DBSession()
        current_order: Order = session.query(Order).filter(Order.order_id == order_id).first()
        if current_order.order_status == "paid":
            return dict(code=0, result="paid")
        else:
            return dict(code=0, result="unpaid")
