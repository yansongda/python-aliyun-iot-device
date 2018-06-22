# aliyun-iot-device-python

非官方，阿里云 IOT 套件设备端 Python 开发 SDK


## 支持的协议

- [x] MQTT
- [x] HTTP
- [ ] CoAP


## 环境

- Python3


## 安装

`pip3 install yansongda-aliyun-iot-device`


## 使用

### MQTT

```Python
from aliyun_iot_device.mqtt import Client as IOT
import time


def on_connect(client, userdata, flags, rc):
    print('subscribe')
    client.subscribe(qos=1)


def on_message(client, userdata, msg):
    print('receive message')
    print(str(msg.payload))


PRODUCE_KEY = "b1VzFx30hEm"
DEVICE_NAME = "iot_device_01"
DEVICE_SECRET = "3TSqd6sfzjSkSwEmLmcAdZnI0oGlmRZ8"

iot = IOT((PRODUCE_KEY, DEVICE_NAME, DEVICE_SECRET))

iot.on_connect = on_connect
iot.on_message = on_message

iot.connect()

iot.loop_start()
while True:
    iot.publish(payload="success", qos=1)
    time.sleep(5)
```

#### 回调

- on_connect

    定义连接成功后的回调函数

    回调函数格式:
    
    `connect_callback(client, userdata, flags, rc)`
        
    client:     the client instance for this callback

    userdata:   the private user data as set in Client() or userdata_set()

    flags:      response flags sent by the broker

    rc:         the connection result

- on_subscribe

    定义订阅成功后的回调函数
    
    回调函数格式:
    
    `subscribe_callback(client, userdata, mid, granted_qos)`

    client:         the client instance for this callback

    userdata:       the private user data as set in Client() or userdata_set()

    mid:            matches the mid variable returned from the corresponding
                    subscribe() call.

    granted_qos:    list of integers that give the QoS level the broker has
                    granted for each of the different subscription requests.

- on_message

    定义收到消息时的回调函数.
    
    回调函数格式:
    
    `on_message_callback(client, userdata, message)`
    
    client:     the client instance for this callback

    userdata:   the private user data as set in Client() or userdata_set()

    message:    an instance of MQTTMessage.This is a class with members topic, payload, qos, retain.


- on_publish

    定义 publish() 方法成功发送消息时的回调函数.
    
    格式:

    `on_publish_callback(client, userdata, mid)`
        
    client:     the client instance for this callback

    userdata:   the private user data as set in Client() or userdata_set()

    mid:        matches the mid variable returned from the corresponding publish() call, to allow outgoing messages to be tracked.

- on_unsubscribe

    定义取消订阅某条 topic 时的回调函数.
    
    格式:

    `unsubscribe_callback(client, userdata, mid)`
        
    client:     the client instance for this callback

    userdata:   the private user data as set in Client() or userdata_set()

    mid:        matches the mid variable returned from the corresponding
                unsubscribe() call.

- on_disconnect

    定义连接断开时的回调函数.
    
    格式:
    
    `disconnect_callback(client, userdata, self)`
        
    client:     the client instance for this callback

    userdata:   the private user data as set in Client() or userdata_set()

    rc:         the disconnection result.

#### 说明

-  域名直连与 HTTPS 认证

    SDK 默认使用域名直连同时启用 TLS 加密。

    如果您不想使用 TLS 加密，可在初始化时传入 `tls=False` 参数；

    如果您想使用 HTTPS 认证，可在初始化时传入 `domain_direct=False` 参数，HTTPS 认证将强制使用 TLS 认证加密

- TLS 认证 CA 证书

    SDK 默认使用了阿里云 IOT 根证书，一般情况无需修改。

    如一定要修改，请传入 `ca_certs="/path/to/cert/root.cer"` 

- websocket 通道

    SDK 默认使用 TCP 通道。

    如果需要使用 websocket，请传入 `transport="websockets"`。

    当使用 websocket 时，默认启用 TLS，即使用的是 wss 协议，如果不想使用 wss，请同时传入 `tls=False`

### HTTP

```Python
from aliyun_iot_device.http import Client as IOT
import time

PRODUCE_KEY = "b1VzFx30hEm"
DEVICE_NAME = "iot_device_01"
DEVICE_SECRET = "3TSqd6sfzjSkSwEmLmcAdZnI0oGlmRZ8"

iot = IOT((PRODUCE_KEY, DEVICE_NAME, DEVICE_SECRET))

while True:
    iot.publish('success')
    time.sleep(5)
```

#### 注意

- 使用 http 协议进行通讯时，需要 token 进行认证，SDK 默认使用内存型缓存（cachetools 方案）进行 token 的保存。

- 如果您需要自行进行其他方案进行保存（file/memcached/redis），可以 `iot.get_token(cache=False)` 获取 token，再 publish 消息时，请 `iot.publish(payload=payload, token=token)`


## 设备影子系统

```Python
# 设备主动上报状态
iot.publish(payload={"method": "update",
                     "version": i,
                     "reported": {"online": True}},
            topic="shadow",
            qos=1)

# 设备主动获取设备影子内容
iot.publish(payload={"method": "get"},
            topic="shadow",
            qos=1)

# 设备端删除影子属性
iot.publish(payload={"method": "delete", "reported": "null"},
            topic="shadow",
            qos=1)
```