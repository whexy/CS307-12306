import datetime

from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_restful import Resource

from model.Database import DBSession
from model.models import User


class SignupApi(Resource):
    """
    API class for user sign-up
    """
    def post(self):
        """
        Sign-up API

        The body should be a JSON dictionary including the following attribute(s):
         - `username`: `str`
         - `real_name`: `str`
         - `password`: `str`
         - `id_card`: `str`
         - `phone_number`: `str`
         - `email`: `str`

        **return**: A JSON dictionary with values:
         - `code`: `int`, equals to 0 if sign-up is successful
         - `error`: `str`, shown if `code != 0`
        """
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
        except:
            session.rollback()
            return jsonify(code=10, error='Unexpected error when creating user')
        finally:
            session.close()


class UserInfoApi(Resource):
    """
    API class for user information operations
    """
    def post(self):
        """
        Login API

        The body should be a JSON dictionary including the following attribute(s):
         - `username`: `str`
         - `password`: `str`

        **return**: A JSON dictionary with values:
         - `code`: `int`, equals to 0 if login is successful
         - `token`: `str` representing JWT token, shown if `code == 0`
         - `error`: `str`, shown if `code != 0`
        """
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
        except:
            return jsonify(code=10, error='Login error')
        finally:
            session.close()

    @jwt_required
    def get(self):
        """
        User information query API, **JWT required**

        **return**: A JSON dictionary with values:
         - `code`: `int`, equals to 0 if query is successful
         - `result`: `dict` containing user information, shown if `code == 0`
         - `error`: `str`, shown if `code != 0`
        """
        session = DBSession()
        try:
            user_id = get_jwt_identity()
            user = session.query(User).filter(User.user_id == user_id).first()
            if user is None:
                return jsonify(error='User not found', code=404)
            return jsonify(result=user.to_dict(), code=0)
        except:
            return jsonify(code=10, error='User information query error')
        finally:
            session.close()

    @jwt_required
    def patch(self):
        """
        User information update API, **JWT required**

        The body should be a JSON dictionary including the following attribute(s):
         - `username`: `str`
         - `password`: `str`
         - `new_password`: `str`
         - `real_name`: `str`
         - `email`: `str`
         - `phone_number`: `str`

        **return**: A JSON dictionary with values:
         - `code`: `int`, equals to 0 if update is successful
         - `error`: `str`, shown if `code != 0`
         - `result`: `str`, shown if `code == 0`
        """
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
            return jsonify(code=0, result='用户信息修改成功')
        except:
            session.rollback()
            return jsonify(code=10, error='Update failed')
        finally:
            session.close()


class UserCheckApi(Resource):
    """
    API class for user existence check
    """
    def get(self):
        """
        User existence check API (check by username)

        **argument**:
         - `username`: `str`

        **return**: A JSON dictionary with values:
        - `code`: `int`, always equals to 0
        - `result`: `boolean` indicating if the user exists
        """
        session = DBSession()
        try:
            username = request.args.get('username')
            user = session.query(User).filter(User.username == username).first()
            return jsonify(result=(user is None), code=0)
        except:
            return jsonify(code=10, error='Query error')
        finally:
            session.close()
