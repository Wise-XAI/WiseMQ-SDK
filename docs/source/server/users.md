用户
=============
WiseAgent致力于隔离并保护用户隐私，因此第三方网站无需提供任何用户信息与WiseMQ进行对接，两者通过唯一的凭证进行关联，你可以创建一张表与原本的用户表进行一对一关联，然后定义字段`wisemq_token`在此自动生成用户的凭证，通过此凭证与WiseAgent进行交互创建WiseAgent用户，而之后有关此用户的所有请求均通过此凭证进行交互。

## 1. 创建用户：`create_wisemq_user`
`create_wisemq_user`方法接收`token`参数进行交互，`token`为网站自定义的用户凭证，
所以定义字典`{"token": "Your User Token"}`传入`create_wisemq_user()`即可。

### 使用样例
```python
import os
# 获取APIKEY与WiseAgent服务地址
APIKEY = os.environ.get("APIKEY")
WiseMQServer = os.environ.get("WiseMQServer")
# 实例化交互对象
wisemq_interface = WiseMQInterface(APIKEY, WiseMQServer)
# 定义所创建的用户凭证
data = {"token": "Your User Token"}
# 发送请求进行交互
wisemq_interface.create_wisemq_user(data)
```

### 返回样例
```
{
    "username": "{{ Username }}",
    "password": "{{ Password }}",
    "token": "{{ Your User Token }}",
    "expired_date": "{{ User Expired Date }}",
    "created": "{{ User Created Date }}"
}
```

## 2. 获取用户信息：`get_user_info`
`get_user_info`方法接收凭证作为权限校验，传入所要获取的用户凭证获取其相关信息。
### 使用样例
```python
...
# 发送请求进行交互
wisemq_interface.get_user_info(token)
```
### 返回样例
```
{
    "username": "{{ Username }}",
    "password": "{{ Password }}",
    "token": "{{ Your User Token }}",
    "expired_date": "{{ User Expired Date }}",
    "created": "{{ User Created Date }}"
}
```

## 3. 获取用户配置文件：`get_client_config_file`
`get_client_config_file`接收凭证作为权限校验，获取用户的配置文件用于客户端上传数据。

### 使用样例
```python
...
# 发送请求进行交互
wisemq_interface.get_client_config_file(token)

```

###返回样例
返回文件格式，可直接映射为地址给用户下载或取出其中的数据做另外处理。
```python
FileResponse(
    {
        "user": {
                "username": "{{ Username }}", 
                "password": "{{ Password }}"
            }, 
    "dataset": [
            {
                "name": "{{ Data Name }}", 
                "broker": {
                    "host": "{{ Broker Host }}", 
                    "port": "{{ Broker Port }}"
                    }
            }
        ]
    }
    )
```