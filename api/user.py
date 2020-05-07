import datetime

from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_restful import Resource

from model.Database import DBSession
from model.models import User


class SignupApi(Resource):
    def post(self):
        session = DBSession()
        try:
            body = request.get_json()
            if session.query(User).filter(User.username == body.get('username')).first() is not None:
                return jsonify(error='Username already exists', code=406)
            new_user = User(**body)
            new_user.hash_password()
            session.add(new_user)
            session.commit()
            return jsonify(code=0)
        finally:
            session.close()


class UserInfoApi(Resource):
    # Login API
    def post(self):
        session = DBSession()
        try:
            body = request.get_json()
            user = session.query(User).filter(User.username == body.get('username')).first()
            if user is None:
                return jsonify(error='Username not found', code=401)
            authorized = user.check_password(body.get('password'))
            if not authorized:
                return jsonify(error='Wrong password', code=401)
            expires = datetime.timedelta(days=1)
            access_token = create_access_token(identity=str(user.user_id), expires_delta=expires)
            return jsonify(token=access_token, code=0)
        finally:
            session.close()

    # Get user info
    @jwt_required
    def get(self):
        session = DBSession()
        try:
            user_id = get_jwt_identity()
            user = session.query(User).filter(User.user_id == user_id).first()
            if user is None:
                return jsonify(error='User not found', code=404)
            return jsonify(result=user.to_dict(), code=0)
        finally:
            session.close()

    @jwt_required
    def patch(self):
        session = DBSession()
        try:
            body = request.get_json()
            user_id = get_jwt_identity()
            user = session.query(User).filter(User.user_id == user_id).first()
            if user is None:
                return jsonify(error='User not found', code=404)
            authorized = user.check_password(body.get('password'))
            if not authorized:
                return jsonify(error='Wrong password', code=401)
            if user.username != body.get('username'):
                new_username = body.get('username')
                if session.query(User).filter(User.username == new_username).first() is not None:
                    return jsonify(error='Username already exists', code=406)
                user.username = new_username
            user.real_name = body.get('real_name')
            user.email = body.get('email')
            user.phone_number = body.get('phone_number')
            if body.get('new_password'):
                user.password = body.get('new_password')
                user.hash_password()
            session.commit()
            return jsonify(code=0)
        finally:
            session.close()


class UserCheckApi(Resource):
    def get(self):
        session = DBSession()
        try:
            username = request.args.get('username')
            user = session.query(User).filter(User.username == username).first()
            return jsonify(result=(user is None), code=0)
        finally:
            session.close()
