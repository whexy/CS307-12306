from flask import Flask
from flask_restful import Api
from flask_bcrypt import Bcrypt

from api.user import UserApi

app = Flask(__name__)
api = Api(app)
bcrypt = Bcrypt(app)

api.add_resource(UserApi, '/user')
app.run()
