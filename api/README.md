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

## 用户登录相关API

| ID   | 调用方式 | API URL              | 用途         | 参数说明                                 |
| ---- | -------- | -------------------- | ------------ | ---------------------------------------- |
| 1    | GET      | /api/user/username | 获取用户信息 | `username`：用户名                       |
| 2    | POST     | /api/user            | 用户注册     | `username`：用户名，`password`：密码 |
| 3    | PATCH    | /api/user            | 用户修改密码 | `username`：用户名，`password`：密码 |
| 4    | DELETE   | /api/user/username | 删除用户数据 | `username`：用户名                       |

