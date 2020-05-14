from flask import request, jsonify
from flask_restful import Resource

from model.Database import DBSession
from model.models import *


class PurchaseApi(Resource):
    """
    API class for ticket purchase
    """

    def get(self):
        """
        Payment API

        **argument**:
        - `order_id`: `int`

        **return**:
        `Purchase succeeded` or `Purchase failed` or `Already paid`
        """
        session = DBSession()
        try:
            order_id = request.args.get('order_id')
            current_order: Order = session.query(Order).filter(Order.order_id == order_id).first()
            if current_order.order_status == "paid":
                return "Already paid"
            current_order.order_status = "paid"
            session.commit()
            session.flush()
            current_ticket: Ticket = session.query(Ticket).filter(Ticket.ticket_id == current_order.ticket_id).first()
            current_ticket.available = True
            session.commit()
            session.flush()
            return "Purchase succeeded"
        except:
            session.rollback()
            return "Purchase failed"
        finally:
            session.close()

    def post(self):
        """
        Ticket payment status query API

        The body should be a JSON dictionary including the following attribute(s):
        - `order_id`: `int`

        **return**: A JSON dictionary with values:
        - `code`: `int`, always equals to 0
        - `result`: `str`, `paid` or `unpaid`
        """
        session = DBSession()
        try:
            body = request.get_json()
            order_id = body.get("order_id")
            current_order: Order = session.query(Order).filter(Order.order_id == order_id).first()
            if current_order.order_status == "paid":
                return jsonify(code=0, result="paid")
            else:
                return jsonify(code=0, result="unpaid")
        except:
            return jsonify(code=10, error='Query error')
        finally:
            session.close()
