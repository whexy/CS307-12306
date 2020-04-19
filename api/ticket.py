from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource


class TicketApi(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        # 现在这个API是假的
        ticket = [{
            "trainName": 'G456',
            "checkEnter": 'A12',
            "seat": '01车01F座',
            "seatClass": '二等座',
            "departStation": '镇江',
            "departStationEnglish": 'Zhenjiang',
            "arrivalStation": '南京',
            "arrivalStationEnglish": 'Nanjing',
            "price": '￥29.5 镇江南站售',
            "time": '2020年4月18日 07:14',
            "name": '石文轩',
            "idCard": '3211011999****6317',
            "orderId": '123456789098765432101',
            "ticketId": 'Z123456789'
        }] * 4
        return jsonify(code=0, ticket=ticket)
