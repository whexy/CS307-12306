from flask import request
from flask_restful import Resource


class UserApi(Resource):
    def post(self):
        body = request.get_json()
        print(body)  # DEBUG
        return 200

    def get(self, id):
        return "Login Succeeded" + id, 200
