from flask import Flask
from flask_restful import Api

from api.user import UserApi

app = Flask(__name__)
api = Api(app)

api.add_resource(UserApi, '/user')
app.run()
