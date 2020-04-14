from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api

from api.user import LoginApi
from api.user import SignupApi
from api.user import UserInfoApi

app = Flask(__name__)

# APP config
app.config["JWT_SECRET_KEY"] = 'Thi5JWT5ecretKey1sHardT0Gue55'

# APP component
api = Api(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# API
api.add_resource(SignupApi, '/auth/signup')
api.add_resource(LoginApi, '/auth/login')
api.add_resource(UserInfoApi, '/user')
# RunTime
app.run()
