from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from sqlalchemy import func, desc
from sqlalchemy.orm import aliased
from pypinyin import lazy_pinyin, Style

from model.Database import DBSession
from model.models import *


class TicketApi(Resource):
    """
    API class for purchased tickets query
    """
    @jwt_required
    def get(self):
        """
        Purchased tickets query API, **JWT required**

        **return**: A JSON dictionary with values:
         - `code`: `int`, always equals to 0
         - `result`: `list` of dictionaries of ticket information:
          - `orderId`: `int`
          - `price`: `str`
          - `orderStatus`: `str`
          - `ticketId`: `str`
          - `name`: `str`
          - `idCard`: `str`
          - `trainName`: `str`
          - `carriageNumber`: `str`
          - `seat`: `str`
          - `seatNumber`: `str`
          - `seatClass`: `str`
          - `departStation`: `str`
          - `departStationEnglish`: `str`
          - `arrivalStation`: `str`
          - `arrivalStationEnglish`: `str`
          - `time`: `str`
          - `realOrderId`: `str`
          - `checkEnter`: `str`
        """
        session = DBSession()
        try:
            user_id = get_jwt_identity()
            dep_i = aliased(Interval, name='dep_i')
            arv_i = aliased(Interval, name='arv_i')
            dep_s = aliased(Station, name='dep_s')
            arv_s = aliased(Station, name='arv_s')
            tickets = list(map(lambda x: dict(zip(x.keys(), x)),
                               session.query(Order.order_id.label('orderId'),
                                             Order.price,
                                             Order.order_status.label('orderStatus'),
                                             Ticket.ticket_id.label('ticketId'),
                                             User.real_name.label('name'),
                                             User.id_card.label('idCard'),
                                             Train.train_name.label('trainName'),
                                             Seat.carriage_number.label('carriageNumber'),
                                             Seat.seat_number.label('seatNumber'),
                                             SeatType.name.label('seatClass'),
                                             dep_s.station_name.label('departStation'),
                                             arv_s.station_name.label('arrivalStation'),
                                             func.cast(dep_i.dep_datetime, String).label('time'))
                               .join(Ticket, Ticket.ticket_id == Order.ticket_id)
                               .join(User, User.user_id == Order.user_id)
                               .join(Seat, Seat.seat_id == Ticket.seat_id)
                               .join(SeatType, SeatType.seat_type_id == Seat.seat_type_id)
                               .join(dep_i, dep_i.interval_id == Ticket.first_interval)
                               .join(arv_i, arv_i.interval_id == Ticket.last_interval)
                               .join(Train, Train.train_id == dep_i.train_id)
                               .join(dep_s, dep_s.station_id == dep_i.dep_station)
                               .join(arv_s, arv_s.station_id == arv_i.arv_station)
                               .filter(Order.user_id == user_id,
                                       Train.available == True,
                                       dep_s.available == True,
                                       arv_s.available == True,
                                       dep_i.available == True,
                                       arv_i.available == True)
                               .order_by(desc(Order.order_timestamp))
                               .all()))
            for t in tickets:
                t['departStationEnglish'] = ''.join(map(lambda x: x[0].upper() + x[1:],
                                                        lazy_pinyin(t['departStation'], style=Style.NORMAL)))
                t['arrivalStationEnglish'] = ''.join(map(lambda x: x[0].upper() + x[1:],
                                                         lazy_pinyin(t['arrivalStation'], style=Style.NORMAL)))
                t['realOrderId'] = t['orderId']
                t['orderId'] = str(t['orderId']).zfill(21)
                t['ticketId'] = 'Z' + str(t['ticketId']).zfill(9)
                t['price'] = '￥{:.2f} 南方铁路售'.format(t['price'])
                t['checkEnter'] = "9¾"
                if t['seatNumber'].endswith('铺'):
                    t['seat'] = '{:02d}车{}'.format(t['carriageNumber'], t['seatNumber'][:-2].zfill(3))
                else:
                    t['seat'] = '{:02d}车{}座'.format(t['carriageNumber'], t['seatNumber'].zfill(3))
            # # 现在这个API是假的
            # ticket = [{
            #     "trainName": 'G456', [x]
            #     "checkEnter": 'A12', [ ] # 不要了
            #     "seat": '01车01F座', [x]
            #     "seatClass": '二等座', [x]
            #     "departStation": '镇江', [x]
            #     "departStationEnglish": 'Zhenjiang', [x]
            #     "arrivalStation": '南京', [x]
            #     "arrivalStationEnglish": 'Nanjing', [x]
            #     "price": '￥29.5 南方铁路售', [x]
            #     "time": '2020年4月18日 07:14', [x]
            #     "name": '石文轩', [x]
            #     "idCard": '3211011999****6317', [x]
            #     "orderId": '123456789098765432101', [x]
            #     "ticketId": 'Z123456789' [x]
            # }] * 4
            return jsonify(code=0, ticket=tickets)
        except:
            return jsonify(code=10, error='Query error')
        finally:
            session.close()
