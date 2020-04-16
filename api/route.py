from api.locate import GeoApi
from api.query import QueryApi, QueryApiV2, QueryApiV3
from api.user import UserInfoApi, SignupApi


def initialize_routes(api):
    api.add_resource(SignupApi, '/signup')
    api.add_resource(UserInfoApi, '/user')
    api.add_resource(GeoApi, '/geo')
    api.add_resource(QueryApi, '/query')
    api.add_resource(QueryApiV2, '/query/v2')
    api.add_resource(QueryApiV3, '/query/v3')
