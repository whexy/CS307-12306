from flask import Flask
from flask_restful import Api
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://checker:123456@121.36.40.215/cs307')
DBSession = sessionmaker(bind=engine)
app = Flask(__name__)
api = Api(app)
from api.user import UserApi

api.add_resource(UserApi, '/user')
app.run()
