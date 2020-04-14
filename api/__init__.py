from api.user import UserApi


def initialize_routes(api):
 api.add_resource(UserApi, '/user/<id>')