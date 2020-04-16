from api.locate import GeoApi
from api.user import UserInfoApi, SignupApi


def initialize_routes(api):
    api.add_resource(SignupApi, '/signup')
    api.add_resource(UserInfoApi, '/user')
    api.add_resource(GeoApi, '/geo')
