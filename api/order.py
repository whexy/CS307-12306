import urllib

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource

from model.Database import DBSession
from model.models import User


class Order(Resource):
    @jwt_required
    def post(self):
        body = request.get_json()
        user_id = get_jwt_identity()
        session = DBSession()
        user = session.query(User).filter(User.user_id == user_id).first()
        train_name = urllib.parse.unquote(request.args.get('train_name'))
        first_interval = int(urllib.parse.unquote(request.args.get('first_interval')))
        last_interval = int(urllib.parse.unquote(request.args.get('last_interval')))
        seat_class = urllib.parse.unquote(request.args.get('seat_class'))
