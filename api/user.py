from flask import request
from flask_restful import Resource

from app import DBSession
from model.models import User


class UserApi(Resource):
    def post(self):
        body = request.get_json()
        new_user = User(**body)
        session = DBSession()
        session.add(new_user)
        session.commit()
        print(body)  # DEBUG
        return 200
