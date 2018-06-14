# -*- coding: utf-8 -*-

__author__ = "yansongda <me@yansongda.cn>"

import paho.mqtt.client as mqtt_client
import hashlib
import hmac
import time
import os

DOMAIN_DIRECT_URI = "{product_key}.iot-as-mqtt.{region}.aliyuncs.com"
DOMAIN_DIRECT_PORT = 1883

WEBSOCKETS_URI = "{product_key}.iot-as-mqtt.{region}.aliyuncs.com"
WEBSOCKETS_PORT = 443

HTTPS_AUTH = "https://iot-auth.{region}.aliyuncs.com/auth/devicename"

DEFAULT_PUBLISH_TOPIC = "/{product_key}/{device_name}/update"
DEFAULT_SUBSCRIBE_TOPIC = "/{product_key}/{device_name}/get"

SHADOW_UPDATE_TOPIC = "/shadow/update/{product_key}/{device_name}"
SHADOW_GET_TOPIC = "/shadow/get/{product_key}/{device_name}"

KEEPALIVE = 60
CA_CERTS = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'root.cer')


class Client(mqtt_client.Client):
    """阿里云 IOT 物联网套件设备端 MQTT 客户端 SDK

    基本使用方法:

    from aliyun_iot_device.mqtt import Client
    iot = Client((PRODUCE_KEY, DEVICE_NAME, DEVICE_SECRET), CLIENT_ID)
    iot.connect()
    iot.loop_start()
    while True:
        iot.publish('success', 1)
        time.sleep(5)
    """

    def __init__(self, product_device, client_id=None, clean_session=True,
                 region="cn-shanghai", domain_direct=True, tls=True, ca_certs=CA_CERTS, transport="tcp"):
        """product_device: (tuple) 阿里云规定三元组，分别为 PRODUCE_KEY, DEVICE_NAME, DEVICE_SECRET

        client_id: (None, str) 客户端 id，如果为 None 或者 ""，则 SDK 自动设置为 DEVICE_NAME

        region: (str) 阿里云地域，目前有cn-shanghai，us-west-1，ap-southeast-1

        domain_direct: (bool) 是否启用域名直连模式，默认启用

        tls: (bool) 是否启用 tls 加密，默认启用

        ca_certs: (str) ca 证书路径，SDK 已默认加载阿里云根证书，无特殊用途不需要更改

        transport: (str) 传输模式，默认为 tcp，支持 websockets
        """
        if not isinstance(product_device, tuple):
            raise TypeError('{pd} Must Be A Tuple'.format(pd=product_device))

        if client_id is None or client_id == "":
            client_id = product_device[1]

        self.client_id = client_id
        self.region = region
        self.tls = tls
        self.ca_certs = ca_certs
        self.domain_direct = domain_direct
        self.transport = transport
        self.clean_session = clean_session
        self.mqtt_uri = ''
        self.mqtt_port = 0
        self.product_key, self.device_name, self.device_secret = product_device

        self._get_mqtt_client()

    def connect(self, keepalive=KEEPALIVE):
        """连接阿里云 IOT 服务器

        keepalive: (int) 心跳秒数，60-300，默认 60秒
        """
        return super(Client, self).connect(self.mqtt_uri, self.mqtt_port, keepalive)

    def publish(self, payload=None, qos=0, topic=None):
        """payload: (str/int/float/None) 负载

        qos: (int) 0/1，服务等级

        topic: (string) 发布的主题。
                如果为 None 默认为阿里云默认主题，即："/{product_key}/{device_name}/update"；

                如果为'shadow'，则为阿里云影子系统主题，即"/shadow/get/{product_key}/{device_name}"，此时payload 应为 dict 类型，包含"version", "reported" 两个key。详情请查看阿里云物联网套件官方文档。

        阿里云 IOT 套件不支持 retain
        """
        if topic is None:
            topic = DEFAULT_PUBLISH_TOPIC.format(product_key=self.product_key, device_name=self.device_name)
        if topic == 'shadow':
            import json
            topic = SHADOW_UPDATE_TOPIC.format(product_key=self.product_key, device_name=self.device_name)

            data = {"method": payload['method']}
            if 'reported' in payload:
                data.update({"state": {"reported": payload['reported']}})
            if 'version' in payload:
                data.update({"version": payload['version']})
            payload = json.dumps(data)

        return super(Client, self).publish(topic, payload, qos, False)

    def subscribe(self, qos=0, topic=None):
        """qos: (int) 0/1，服务等级

        topic: (string) 订阅的主题。
                如果为 None 默认为阿里云默认主题，即："/{product_key}/{device_name}/get"；
                如果为'shadow'，则为阿里云影子系统主题，即"/shadow/get/{product_key}/{device_name}"
        """
        if topic is None:
            topic = DEFAULT_SUBSCRIBE_TOPIC.format(product_key=self.product_key, device_name=self.device_name)
        if topic == 'shadow':
            topic = SHADOW_GET_TOPIC.format(product_key=self.product_key, device_name=self.device_name)

        return super(Client, self).subscribe(topic, qos)

    def unsubscribe(self, topic=None):
        """topic: (string) 订阅的主题，默认为阿里云默认主题，即："/{product_key}/{device_name}/get"
        """
        if topic is None:
            topic = DEFAULT_SUBSCRIBE_TOPIC.format(product_key=self.product_key, device_name=self.device_name)

        return super(Client, self).unsubscribe(topic)

    def _get_mqtt_client(self):
        """获取 MQTT 客户端实例
        """
        if self.transport == "websockets":
            mqtt_client_id, mqtt_user, mqtt_passwd = self._get_websockets_mqtt_info()
        elif self.domain_direct:
            mqtt_client_id, mqtt_user, mqtt_passwd = self._get_doamin_direct_mqtt_info()
        else:
            mqtt_client_id, mqtt_user, mqtt_passwd = self._get_https_mqtt_info()

        super(Client, self).__init__(mqtt_client_id, transport=self.transport, clean_session=self.clean_session)
        self.username_pw_set(mqtt_user, mqtt_passwd)
        if not self.domain_direct or self.tls:
            self.tls_set(ca_certs=self.ca_certs)

    def _get_doamin_direct_mqtt_info(self):
        """获取域名直连 MQTT 连接信息
        """
        mode = "3"
        if self.tls:
            mode = "2"

        mqtt_client_id = self.client_id + "|securemode=" + mode + ",signmethod=hmacsha1,timestamp=" + str(round(time.time())) + "|"
        mqtt_user = self.device_name + "&" + self.product_key
        mqtt_content = "clientId" + self.client_id + "deviceName" + self.device_name + "productKey" + self.product_key + "timestamp" + str(round(time.time()))
        mqtt_passwd = hmac.new(bytes(self.device_secret, 'utf-8'), bytes(mqtt_content, 'utf-8'), hashlib.sha1).hexdigest()

        self.mqtt_uri = DOMAIN_DIRECT_URI.format(product_key=self.product_key, region=self.region)
        self.mqtt_port = DOMAIN_DIRECT_PORT

        return mqtt_client_id, mqtt_user, mqtt_passwd

    def _get_websockets_mqtt_info(self):
        websockets_info = self._get_doamin_direct_mqtt_info()

        self.mqtt_uri = WEBSOCKETS_URI.format(product_key=self.product_key, region=self.region)
        self.mqtt_port = WEBSOCKETS_PORT

        return websockets_info

    def _get_https_mqtt_info(self):
        """获取HTTPS 连接方法 MQTT 连接信息
        """
        import requests

        response = requests.post(HTTPS_AUTH.format(region=self.region),
                                 data={'productKey': self.product_key,
                                       'deviceName': self.device_name,
                                       'clientId': self.client_id,
                                       'signmethod': "hmacsha1",
                                       "resources": "mqtt",
                                       "timestamp": str(round(time.time())),
                                       "sign": self._get_sign()}).json()
        if response['code'] != 200:
            raise ValueError("获取连接信息错误:{}".format(response))

        self.mqtt_uri = response['data']['resources']['mqtt']['host']
        self.mqtt_port = response['data']['resources']['mqtt']['port']

        return self.client_id, response['data']['iotId'], response['data']['iotToken']

    def _get_sign(self):
        content = "clientId" + self.client_id + "deviceName" + self.device_name + "productKey" + self.product_key + "timestamp" + str(round(time.time()))
        return hmac.new(bytes(self.device_secret, 'utf-8'), bytes(content, 'utf-8'), hashlib.sha1).hexdigest()
