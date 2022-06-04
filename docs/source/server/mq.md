数据智能体
=============
在交互创建用户后可创建用户所使用的数据智能体。

## 1. 创建数据智能体：`create_data_agent`
`create_data_agent(token, number_of_data)`，其接收两个参数，第一个为用户凭证，第二个为创建数据智能体的数量。

### 使用样例
```python
import os
# 获取APIKEY与WiseAgent服务地址
APIKEY = os.environ.get("APIKEY")
WiseMQServer = os.environ.get("WiseMQServer")
# 实例化交互对象
wisemq_interface = WiseMQInterface(APIKEY, WiseMQServer)
# 定义所创建的用户凭证和数量
data = {"token": "Your User Token", "number_of_data": "Number of data that supposed to generate"}
# 发送请求进行交互
wisemq_interface.create_data_agent(*data)
```

### 返回样例
```python
[
    {
        "id": "{{ Data ID }}",
        "name": "{{ Data Name }}"
    },
    {
        "id": "{{ Data ID }}",
        "name": "{{ Data Name }}"
    }
]
```

## 2. 获取数据智能体列表：`get_data_agent_list`
`get_data_agent_list`接收用户凭证参数，返回此用户所拥有的所有数据智能体。

### 使用样例
```python
...
# 发送请求进行交互
wisemq_interface.get_data_agent_list(token)
```

### 返回样例
```python
{
    "count": {{ Data Total }},  # int
    "next": null,  # 如果有则返回下一个的链接
    "previous": null,  # 如果有则返回上一个的链接
    "results": [
        {
            "id": {{ Data ID }},  # int
            "name": "{{ Data Name }}",  # str
        },
        {
            "id": {{ Data ID }},  # int
            "name": "{{ Data Name }}",  # str
        },
        ...
    ]
}
```

## 3. 获取数据智能体信息：`get_data_agent_info`
`get_data_agent_info(token, data_pk)`接收用户凭证和智能体ID作为参数，返回数据智能体的具体信息。

### 使用样例
```python
...
# 发送请求进行交互
wisemq_interface.get_data_agent_info(token, data_pk)
```

### 返回样例
```python
{
    "id": {{ Data ID }},  # int
    "name": "{{ Data Name }}",  # str
    "status": {
        "status1": {
            "type": "only_show",  # str,  单纯显示
            "value": "{{ Value }}"  # str
        },
        "status2": {
            "type": "switch",  # str, 开关，客户端可定义回调函数进行使用
            "value": {{ 0 or 1}}  # int, 只有0或1，0，具体含义可自行统一
        },
        ...
    }
}
```

## 4. 获取智能体存储数据：`get_messages`
`get_messages(token, data_pk, limit=None, offset=None)`接收用户凭证和智能体ID作为参数，返回数据智能体中所持久化的数据。

### 使用样例
```python
...
# 发送请求进行交互
wisemq_interface.get_messages(token, data_pk)
```
`get_messages`采用LimitOffsetPagination，通过定义开始位置offset和数量limit可获取数据，数据为倒序输出。

### 返回样例
```python
{
    "count": {{ Data Total }},  # int
    "next": "{{ domain }}/api/v1/mq/{{ token }}/data/{{ data_pk }}/get_messages?limit={{ limit }}&offset={{ offset }}",  # 下一页的地址
    "previous": "{{ domain }}/api/v1/mq/{{ token }}/data/{{ data_pk }}/get_messages?limit={{ limit }}",  # 上一页的地址
    "results": [  # 用户上传数据
        ...
    ]
}
```