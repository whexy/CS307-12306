from flask import request
from flask_restful import Resource

from model.Database import DBSession
from model.models import User


class UserApi(Resource):
    def post(self):
        body = request.get_json()
        new_user = User(**body)
        new_user.hash_password()
        session = DBSession()
        session.add(new_user)
        session.commit()
        print(body)  # DEBUG
        return 200
