import datetime

from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_restful import Resource

from model.Database import DBSession
from model.models import User


class SignupApi(Resource):
    def post(self):
        body = request.get_json()
        new_user = User(**body)
        new_user.hash_password()
        session = DBSession()
        session.add(new_user)
        session.commit()
        print(body)  # DEBUG
        return 200


class LoginApi(Resource):
    def post(self):
        body = request.get_json()
        # user = User.query().filter_by(username=body.get('username')).first()
        session = DBSession()
        user = session.query(User).filter(User.username == body.get('username')).first()
        if user is None:
            return {'error': 'Username not found'}, 401
        authorized = user.check_password(body.get('password'))
        if not authorized:
            return {'error': 'Invalid password'}, 401
        expires = datetime.timedelta(days=1)
        access_token = create_access_token(identity=str(user.user_id), expires_delta=expires)
        return {'token': access_token}, 200


class UserInfoApi(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        session = DBSession()
        user = session.query(User).filter(User.user_id == user_id).first()
        if user is None:
            return {'error': 'User not found'}, 404
        return user.to_dict(), 200

    @jwt_required
    def post(self):
        pass