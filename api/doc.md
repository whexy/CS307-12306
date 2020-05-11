
# api


# api.user


## SignupApi
```python
SignupApi()
```

API class for user sign-up


### methods


### post
```python
SignupApi.post()
```

Sign-up API

The body should be a JSON dictionary including the following attribute(s):
 - `username`: `str`
 - `real_name`: `str`
 - `password`: `str`
 - `id_card`: `str`
 - `phone_number`: `str`
 - `email`: `str`

**return**: A JSON dictionary with values:
 - `code`: `int`, equals to 0 if sign-up is successful
 - `error`: `str`, shown if `code != 0`


## UserInfoApi
```python
UserInfoApi()
```

API class for user information operations


### methods


### post
```python
UserInfoApi.post()
```

Login API

The body should be a JSON dictionary including the following attribute(s):
 - `username`: `str`
 - `password`: `str`

**return**: A JSON dictionary with values:
 - `code`: `int`, equals to 0 if login is successful
 - `token`: `str` representing JWT token, shown if `code == 0`
 - `error`: `str`, shown if `code != 0`


### get
```python
UserInfoApi.get(*args, **kwargs)
```

User information query API, **JWT required**

**return**: A JSON dictionary with values:
 - `code`: `int`, equals to 0 if query is successful
 - `result`: `dict` containing user information, shown if `code == 0`
 - `error`: `str`, shown if `code != 0`


### patch
```python
UserInfoApi.patch(*args, **kwargs)
```

User information update API, **JWT required**

The body should be a JSON dictionary including the following attribute(s):
 - `username`: `str`
 - `password`: `str`
 - `new_password`: `str`
 - `real_name`: `str`
 - `email`: `str`
 - `phone_number`: `str`

**return**: A JSON dictionary with values:
 - `code`: `int`, equals to 0 if update is successful
 - `error`: `str`, shown if `code != 0`
 - `result`: `str`, shown if `code == 0`


## UserCheckApi
```python
UserCheckApi()
```

API class for user existence check


### methods


### get
```python
UserCheckApi.get()
```

User existence check API (check by username)

**argument**:
 - `username`: `str`

**return**: A JSON dictionary with values:
- `code`: `int`, always equals to 0
- `result`: `boolean` indicating if the user exists


# api.ticket


## TicketApi
```python
TicketApi()
```

API class for purchased tickets query


### methods


### get
```python
TicketApi.get(*args, **kwargs)
```

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


# api.route


## initialize_routes
```python
initialize_routes(api)
```

Initializes routes for APIs


# api.query


## QueryApi
```python
QueryApi()
```

API class for train information query _(version 1, deprecated)_


### methods


## QueryApiV2
```python
QueryApiV2()
```

API class for train information query _(version 2 for SQL test, deprecated)_


### methods


## QueryApiV3
```python
QueryApiV3()
```

API class for train information query _(version 3 for station-to-station query, deprecated)_


### methods


## QueryApiV4
```python
QueryApiV4()
```

API class for train information query _(version 4)_


### methods


### get
```python
QueryApiV4.get()
```

Train information query API

**argument**:
 - `dep_station`: `str`
 - `arv_station`: `str`
 - `DG_only`: `boolean`
**return**: A JSON dictionary with values:
 - `code`: `int`, always equals to 0
 - `result`: `list` of dictionaries of train information:
  - `train_name`: `str`
  - `first_interval`: `int`
  - `last_interval`: `int`
  - `dep_station`: `str`
  - `dep_time`: `str`
  - `arv_station`: `str`
  - `arv_time`: `str`


## QueryTransfer
```python
QueryTransfer()
```

API class for transfer station query


### methods


### transfer_list


### get
```python
QueryTransfer.get()
```

Transfer station query API

**argument**:
 - `dep_station`: `str`
 - `arv_station`: `str`
 - `DG_only`: `boolean`

**return**: A JSON dictionary with values:
 - `code`: `int`, always equals to 0
 - `result`: `list` of dictionaries of station information:
  - `stationName`: `str`
  - `stationId`: `int`


## TicketQuery
```python
TicketQuery()
```

API class for available tickets query


### methods


### get
```python
TicketQuery.get()
```

Available tickets query API

**return**: A JSON dictionary with values:
 - `code`: `int`, always equals to 0
 - `result`: `list` of dictionaries of ticket information:
  - `seat_type_id`: `int`
  - `seat_type_name`: `str`
  - `left_cnt`: `int`
  - `price`: `float`


# api.purchase


## PurchaseApi
```python
PurchaseApi()
```

API class for ticket purchase


### methods


### get
```python
PurchaseApi.get()
```

Payment API

**argument**:
 - `order_id`: `int`

**return**:
 `Purchase succeeded` or `Purchase failed` or `Already paid`


### post
```python
PurchaseApi.post()
```

Ticket payment status query API

The body should be a JSON dictionary including the following attribute(s):
 - `order_id`: `int`

**return**: A JSON dictionary with values:
 - `code`: `int`, always equals to 0
 - `result`: `str`, `paid` or `unpaid`


# api.order


## OrderApi
```python
OrderApi()
```

API class for ticket ordering


### methods


### post
```python
OrderApi.post(*args, **kwargs)
```

Train order API, **JWT required**

**return**: A JSON dictionary with values:
 - `code`: `int`, equals to 0 if order is successful
 - `result`: `dict` with values, shown if `code == 0`:
  - `order_id`: `int`
 - `error`: `str`, shown if `code != 0`


### delete
```python
OrderApi.delete(*args, **kwargs)
```

Ticket refund API, **JWT required**

**return**: A JSON dictionary with values:
 - `code`: `int`, equals to 0 if deletion is successful
 - `result`: `str`, shown if `code == 0`
 - `error`: `str`, shown if `code != 0`


# api.locate


## GeoApi
```python
GeoApi()
```

API class for geographic position query


### methods


### get
```python
GeoApi.get()
```

Geographic position query API

**argument**:
 - `geo_name`: `str`

**return**: A JSON dictionary with values:
 - `code`: `int`, always equals to 0
 - `result`: `list` of dictionaries of position information:
  - `province`: `str`
  - `city`: `str`
  - `district`: `str`
  - `station`: `str`


## TrainApi
```python
TrainApi()
```

API class for train information query _(version 1, deprecated)_


### methods


## TrainApiV2
```python
TrainApiV2()
```

API class for train information query _(version 2)_


### methods


### get
```python
TrainApiV2.get()
```

Train information query API

**argument**:
 - `train_name`: `str`

**return**: A JSON dictionary with values:
 - `code`: `int`, always equals to 0
 - `result`: `list` of dictionaries of passing station information:
  - `id`: `int`
  - `district`: `str`
  - `station`: `str`
  - `time`: `str`


## AreaApi
```python
AreaApi()
```

API class for district information query


### methods


### get
```python
AreaApi.get()
```

District information query API

**argument**:
 - `province`: `str`, can be empty
 - `city`: `str`, can be empty if province is not specified
 - `district`: `str`, can be empty if city is not specified

**return**: A JSON dictionary with values:
 - `code`: `int`, always equals to 0
 - `result`: `list` of dictionaries of provinces/cities/districts:
  - `province_name`/`city_name`/`district_name`: `str`


# api.admin


## AdminStationApi
```python
AdminStationApi()
```

API class for station administration


### methods


### post
```python
AdminStationApi.post(*args, **kwargs)
```

Station addition API, **JWT required**

**argument**:
 - `province_name`: `str`
 - `city_name`: `str`
 - `district_name`: `str`
 - `station_name`: `str`

**return**: A JSON dictionary with values
 - `code`: `int`, equals to 0 if addition is successful
 - `result`: `str` for success message, shown if `code == 0`
 - `error`: `str`, shown if `code != 0`


### patch
```python
AdminStationApi.patch(*args, **kwargs)
```

Station modification API, **JWT required**

**argument**:
 - `city_name`: `str`
 - `district_name`: `str`
 - `station_name`: `str`
 - `new_station_name`: `str`

**return**: A JSON dictionary with values
 - `code`: `int`, equals to 0 if modification is successful
 - `result`: `str` for success message, shown if `code == 0`
 - `error`: `str`, shown if `code != 0`


### delete
```python
AdminStationApi.delete(*args, **kwargs)
```

Station deletion API, **JWT required**

**argument**:
 - `station_name`: `str`

**return**: A JSON dictionary with values
 - `code`: `int`, equals to 0 if deletion is successful
 - `result`: `str` for success message, shown if `code == 0`
 - `error`: `str`, shown if `code != 0`


## AdminTrainApi
```python
AdminTrainApi()
```

API class for train administration


### methods


### get
```python
AdminTrainApi.get(*args, **kwargs)
```

Train information query API for administrator, **JWT required**

**argument**:
 - `train_name`: `str`

**return**: A JSON dictionary with values:
 - `code`: `int`, equals to 0 if query is successful
 - `error`: `str`, shown if `code != 0`
 - `result`: `list` of dictionaries of interval information:
  - `interval_id`: `int`
  - `interval_no`： `int`
  - `train_name`: `str`
  - `dep_station`: `str`
  - `arv_station`: `str`
  - `dep_datetime`: `str`
  - `arv_datetime`: `str`
  - `price`: `dict` containing:
   - `seat_type_1`, `str`
   - `seat_type_2`, `str`
   - `seat_type_3`, `str`
   - `seat_type_4`, `str`
   - `seat_type_5`, `str`
   - `seat_type_6`, `str`
   - `seat_type_7`, `str`


### post
```python
AdminTrainApi.post(*args, **kwargs)
```

Train information update API for administrator, **JWT required**

The body should be a JSON dictionary including the following attribute(s):
 - `interval_id`: `int`
 - `price`: `dict` containing:
  - `seat_type_1`, `str`
  - `seat_type_2`, `str`
  - `seat_type_3`, `str`
  - `seat_type_4`, `str`
  - `seat_type_5`, `str`
  - `seat_type_6`, `str`
  - `seat_type_7`, `str`


**return**: A JSON dictionary with values:
 - `code`: `int`, equals to 0 if update is successful
 - `error`: `str`, shown if `code != 0`
 - `result`: `str`, shown if `code == 0`

