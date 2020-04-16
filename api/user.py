import datetime

from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_restful import Resource

from model.Database import DBSession
from model.models import User


class SignupApi(Resource):
    def post(self):
        body = request.get_json()
        session = DBSession()
        if session.query(User).filter(User.username == body.get('username')).first() is not None:
            return {'error': 'Username already exists!'}, 406
        new_user = User(**body)
        new_user.hash_password()
        session.add(new_user)
        session.commit()
        return 200


class UserInfoApi(Resource):
    def post(self):
        body = request.get_json()
        session = DBSession()
        user = session.query(User).filter(User.username == body.get('username')).first()
        if user is None:
            return {'error': 'Username not found'}, 401
        authorized = user.check_password(body.get('password'))
        if not authorized:
            return {'error': 'Wrong password'}, 401
        expires = datetime.timedelta(days=1)
        access_token = create_access_token(identity=str(user.user_id), expires_delta=expires)
        return {'token': access_token}, 200

    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        session = DBSession()
        user = session.query(User).filter(User.user_id == user_id).first()
        if user is None:
            return {'error': 'User not found'}, 404
        return user.to_dict(), 200

    @jwt_required
    def patch(self):
        body = request.get_json()
        user_id = get_jwt_identity()
        session = DBSession()
        user = session.query(User).filter(User.user_id == user_id).first()
        if user is None:
            return {'error': 'User not found'}, 404
        authorized = user.check_password(body.get('password'))
        if not authorized:
            return {'error': 'Wrong password'}, 401
        if user.username != body.get('username'):
            new_username = body.get('username')
            if session.query(User).filter(User.username == new_username).first() is not None:
                return {'error': 'Username already exists!'}, 406
            user.username = new_username
        user.real_name = body.get('real_name')
        user.email = body.get('email')
        user.phone_number = body.get('phone_number')
        if body.get('new_password'):
            user.password = body.get('new_password')
            user.hash_password()
        session.commit()


class UserCheckApi(Resource):
    def get(self):
        username = request.args.get('username')
        session = DBSession()
        user = session.query(User).filter(User.username == username).first()
        return jsonify(result=(user is None))
