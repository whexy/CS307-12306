from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api

from api.route import initialize_routes

app = Flask(__name__)

# APP config
app.config["JWT_SECRET_KEY"] = 'Thi5JWT5ecretKey1sHardT0Gue55'

# APP component
api = Api(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# API
initialize_routes(api)

if __name__ == '__main__':
    # RunTime
    app.run()
