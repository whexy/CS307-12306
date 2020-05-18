from locust import task, TaskSet, HttpUser, between
import json

# 12307 内部压力测试
# 测试时间：上线前3天
# 测试内容：服务器对订票的并发处理
# 测试员： Whexy
# 测试结果： 很差

headers = {
    "Content-type": "application/json",
    "Authorization": "Bearer {}".format(
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODk3MDg0MDMsIm5iZiI6MTU4OTcwODQwMywianRpIjoiZDg3NWIzMjctMjg2MS00NDhiLWI2NDYtMWYxMzc0Yzc4NzgwIiwiZXhwIjoxNTg5Nzk0ODAzLCJpZGVudGl0eSI6IjExIiwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.AMVgdgh3DzgXSttQ3OwXG1Tu0CkG0YaRSBq1CzwRYQ8")
}

train = dict(
    train_name="G1257", first_interval=170257, last_interval=170257
)


class UserTasks(TaskSet):
    @task(1)
    def order_and_purchase(self):
        resp = self.client.post('/order', headers=headers, data=json.dumps({
            'seat_class': 1,
            'train_name': train["train_name"],
            'first_interval': train["first_interval"],
            'last_interval': train["last_interval"]
        })).json()
        if resp['code'] != 0:
            raise Exception('Order:', resp['error'])
        order_id = resp['result']['order_id']
        resp = self.client.get('/purchase?order_id={}'.format(order_id), headers=headers)
        if resp.text.strip() != '"Purchase succeeded"':
            print(resp.text)
            raise Exception("Purchase failed")
        return order_id


class WebsiteUser(HttpUser):
    host = "http://121.36.40.215:12307"
    tasks = [UserTasks]
    wait_time = between(5.0, 9.0)
