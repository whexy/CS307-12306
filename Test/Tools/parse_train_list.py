import json

if __name__ == '__main__':
    with open('../../Resources/train_list.js', 'r') as js:
        content = js.read()[16:]
        js_dict = json.loads(content)
    print(js_dict.keys())
    print(js_dict['2019-10-10'].keys())
    print(js_dict['2019-10-10']['D'])
    with open('../../Resources/train_info_list.csv', 'w') as csv:
        csv.write('date,type,station_train_code,train_no\n')
        for date in js_dict.keys():
            js_date_dict = js_dict[date]
            for train_type in js_date_dict.keys():
                train_list = js_date_dict[train_type]
                for train in train_list:
                    csv.write("{},{},{},{}\n".format(date, train_type, train['station_train_code'], train['train_no']))
