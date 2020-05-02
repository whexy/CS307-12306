# 项目 API 手册
CS307-12306的后端被设计为与数据库交互的、纯粹的Restful API。
作为《数据库原理》课程的项目。后端不应该有太多逻辑。

*两个人的项目实在太肝了。给我们面试的时候加点分吧😀️*


# 项目 API 设计规则
- 所有逻辑上的变动必须在设计文本上有所展现。
- API服务用户订票系统和公司管理系统。这两个系统功能上相关，重复的功能只应提供一个API。
- 尽量按照Restful的思想设计API。
    - GET（SELECT）：从服务器取出资源（一项或多项）。
    - POST（CREATE）：在服务器新建一个资源。
    - PUT（UPDATE）：在服务器更新资源（客户端提供改变后的完整资源）。
    - PATCH（UPDATE）：在服务器更新资源（客户端提供改变的属性）。
    - DELETE（DELETE）：从服务器删除资源。

# API 说明
这是第一版API的设计规则。全面的API设定如下。

订票API

- 接收 list POST：
  - 火车信息 train_name
  - 区间信息 from_station, to_station
  - 座位信息 prefer_seat_type[]
  - 舱位等级信息 seat_class
- 返回：
  - 是否成功 is_success
- 后台操作 if success：
  - 添加ticket(s)/order(s)
  - 占用seat



订单查询API

- 接收 GET
- 返回 list：
  - 订单号 order_id
  - 票号 ticket_id
  - 火车/站点信息 train_name, dep_station, arv_station
  - 座位信息 seat, seat_class
  - 出发时间 time
  - 价格 price
  - 乘客信息 name, id_card, ...



余票查询API

- 接收 GET：
  - 城市信息 from_city, to_city
  - 只查动车/高铁 DG_only: bool
- 返回 list（直达）：
  - 火车号 train_name
  - 车站信息 dep_station, arv_station
  - 时间 dep_time, arv_time
  - 各舱位余票 ticket_left[]
