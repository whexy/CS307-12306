from api.locate import GeoApi, TrainApi, TrainApiV2
from api.query import QueryApi, QueryApiV2, QueryApiV3
from api.ticket import TicketApi
from api.user import UserInfoApi, SignupApi, UserCheckApi


def initialize_routes(api):
    api.add_resource(SignupApi, '/signup')
    api.add_resource(UserInfoApi, '/user')
    api.add_resource(GeoApi, '/geo')
    api.add_resource(QueryApi, '/query')
    api.add_resource(QueryApiV2, '/query/v2')
    api.add_resource(QueryApiV3, '/query/v3')
    api.add_resource(UserCheckApi, '/user/check')
    api.add_resource(TicketApi, '/ticket')
    api.add_resource(TrainApi, '/train')
    api.add_resource(TrainApiV2, '/train/v2')
