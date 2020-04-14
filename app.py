from flask import Flask

from api.user import user_api

app = Flask(__name__)
app.register_blueprint(user_api, url_prefix="/user")
app.run()
