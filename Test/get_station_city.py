import requests
import json


def gao():
    with open('../Resources/车站.txt', 'r') as chezhan:
        chezhan_list = chezhan.read().split('\n')
    with open('../Resources/station_city.csv', 'w') as csv:
        csv.write('station,province,city,district\n')
        for s in chezhan_list:
            c = requests.get(
                'https://restapi.amap.com/v3/geocode/geo?key={}&address={}'.format('b940f83a96d4391b0f20e08770cda1a7',
                                                                                   s)).text
            j = json.loads(c)
            g = j['geocodes']
            if g:
                csv.write('{},{},{},{}\n'.format(s, g[0]['province'], g[0]['city'], g[0]['district']))
            else:
                c = requests.get('https://restapi.amap.com/v3/geocode/geo?key={}&address={}'.format(
                    'b940f83a96d4391b0f20e08770cda1a7', s + '站')).text
                j = json.loads(c)
                g = j['geocodes']
                if g:
                    csv.write('{},{},{},{}\n'.format(s, g[0]['province'], g[0]['city'], g[0]['district']))
                else:
                    print(s, j)


def gao1():
    with open('../Resources/没查到的.txt', 'r') as fin:
        cha = list(map(lambda x: x.split()[0], fin.read().splitlines()))
    with open('../Resources/station_city.csv', 'a') as csv:
        for s in cha:
            c = requests.get(
                'https://restapi.amap.com/v3/geocode/geo?key={}&address={}'.format('b940f83a96d4391b0f20e08770cda1a7',
                                                                                   s + '火车站')).text
            j = json.loads(c)
            g = j['geocodes']
            if g:
                csv.write('{},{},{},{}\n'.format(s, g[0]['province'], g[0]['city'], g[0]['district']))
            else:
                c = requests.get('https://restapi.amap.com/v3/geocode/geo?key={}&address={}'.format(
                    'b940f83a96d4391b0f20e08770cda1a7', s + '车站')).text
                j = json.loads(c)
                g = j['geocodes']
                if g:
                    csv.write('{},{},{},{}\n'.format(s, g[0]['province'], g[0]['city'], g[0]['district']))
                else:
                    print(s)


if __name__ == '__main__':
    gao1()
