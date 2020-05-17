from requests import request
import json
import time

base_url = 'http://127.0.0.1:5000'
headers = {'Content-Type': 'application/json'}


def login():
    user_info = {'username': 'HWJ', 'password': 'HWJ'}
    resp = request('POST', base_url + '/user', headers=headers, data=json.dumps(user_info)).json()
    if resp['code'] != 0:
        raise Exception('Login:', resp['error'])
    print(resp)
    headers.update({'Authorization': 'bearer ' + resp['token']})


def get_train_list():
    dep_station = '成都'
    arv_station = '重庆'
    resp = request('GET',
                   base_url + '/query/v4?dep_station={}&arv_station={}&DG_only=true'.format(dep_station, arv_station),
                   headers=headers).json()
    if resp['code'] != 0:
        raise Exception('Query train list:', resp['error'])
    return resp['result']


def query_left_ticket(train_name, first_interval, last_interval):
    resp = request('GET', base_url + '/query/ticket?train_name={}&first_interval={}&last_interval={}'.format(
        train_name, first_interval, last_interval), headers=headers).json()
    if resp['code'] != 0:
        raise Exception('Query left tickets:', resp['error'])
    seat_list = resp['result']
    for seat in seat_list:
        if seat['seat_type_id'] == 2:
            return seat['left_cnt']
    return 0


def order_and_purchase(train_name, first_interval, last_interval):
    resp = request('POST', base_url + '/order', headers=headers, data=json.dumps({
        'seat_class': 2,
        'train_name': train_name,
        'first_interval': first_interval,
        'last_interval': last_interval
    })).json()
    if resp['code'] != 0:
        raise Exception('Order:', resp['error'])
    order_id = resp['result']['order_id']
    resp = request('GET', base_url + '/purchase?order_id={}'.format(order_id), headers=headers).json()
    if resp['code'] != 0:
        raise Exception('Payment:', resp['error'])
    return order_id


def main():
    time_list = []
    try:
        login()
        train_list = get_train_list()
        for train in train_list:
            print('Purchasing', train['train_name'])
            while query_left_ticket(train['train_name'], train['first_interval'], train['last_interval']) > 1:
                begin_time = time.time()
                order_id = order_and_purchase(train['train_name'], train['first_interval'], train['last_interval'])
                end_time = time.time()
                print('Order #{}: {:.3f}s'.format(order_id, end_time - begin_time))
                time_list.append(end_time - begin_time)
    finally:
        print('max: {}, min: {}, average: {}'.format(max(time_list), min(time_list), sum(time_list) / len(time_list)))


if __name__ == '__main__':
    login()
