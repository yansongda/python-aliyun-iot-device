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

KEEPALIVE = 60
CA_CERTS = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'root.cer')


class Client(object):
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

    def __init__(self, product_device, client_id=None,
                 region="cn-shanghai", domain_direct=True, tls=True, ca_certs=CA_CERTS, transport="tcp"):
        """product_device: (tuple) 阿里云规定三元组，分别为 PRODUCE_KEY, DEVICE_NAME, DEVICE_SECRET

        client_id: (None, str) 客户端 id，如果为 None 或者 ""，则 SDK 自动设置为当前毫秒时间戳

        region: (str) 阿里云地域，目前有cn-shanghai，us-west-1，ap-southeast-1

        domain_direct: (bool) 是否启用域名直连模式，默认启用

        tls: (bool) 是否启用 tls 加密，默认启用

        ca_certs: (str) ca 证书路径，SDK 已默认加载阿里云根证书，无特殊用途不需要更改

        transport: (str) 传输模式，默认为 tcp，支持 websockets
        """
        super(Client, self).__init__()
        if not isinstance(product_device, tuple):
            raise TypeError('{pd} Must Be A Tuple'.format(pd=product_device))

        if client_id is None or client_id == "":
            client_id = str(round(time.time() * 1000))

        self.client_id = client_id
        self.region = region
        self.tls = tls
        self.ca_certs = ca_certs
        self.domain_direct = domain_direct
        self.transport = transport
        self.product_key, self.device_name, self.device_secret = product_device

        self.mqtt = self._get_mqtt_client()

    def connect(self, keepalive=KEEPALIVE):
        """连接阿里云 IOT 服务器

        keepalive: (int) 心跳秒数，60-300，默认 60秒
        """
        return self.mqtt.connect(self.mqtt_uri, self.mqtt_port, keepalive)

    def publish(self, payload=None, qos=0, retain=False, topic=None):
        """payload: (str/int/float/None) 负载

        qos: (int) 0/1，服务等级

        topic: (string) 发布的主题，默认为阿里云默认主题，即："/{product_key}/{device_name}/update"

        retain: (bool) If set to true, the message will be set as the "last known
        good"/retained message for the topic.
        """
        if topic is None:
            topic = DEFAULT_PUBLISH_TOPIC.format(product_key=self.product_key, device_name=self.device_name)

        return self.mqtt.publish(topic, payload, qos, retain)

    def subscribe(self, qos=0, topic=None):
        """qos: (int) 0/1，服务等级

        topic: (string) 订阅的主题，默认为阿里云默认主题，即："/{product_key}/{device_name}/get"
        """
        if topic is None:
            topic = DEFAULT_SUBSCRIBE_TOPIC.format(product_key=self.product_key, device_name=self.device_name)

        return self.mqtt.subscribe(topic, qos)

    def unsubscribe(self, topic=None):
        """topic: (string) 订阅的主题，默认为阿里云默认主题，即："/{product_key}/{device_name}/get"
        """
        if topic is None:
            topic = DEFAULT_SUBSCRIBE_TOPIC.format(product_key=self.product_key, device_name=self.device_name)

        return self.mqtt.unsubscribe(topic)

    def loop_start(self):
        """在处理循环逻辑开始前，请先调用此方法。此方法会自动处理心跳，流入数据等
        """
        return self.mqtt.loop_start()

    def loop_stop(self, force=False):
        return self.mqtt.loop_stop(force)

    def _get_mqtt_client(self):
        """获取 MQTT 客户端实例
        """
        if self.transport == "websockets":
            mqtt_client_id, mqtt_user, mqtt_passwd = self._get_websockets_mqtt_info()
        elif self.domain_direct:
            mqtt_client_id, mqtt_user, mqtt_passwd = self._get_doamin_direct_mqtt_info()
        else:
            mqtt_client_id, mqtt_user, mqtt_passwd = self._get_https_mqtt_info()

        mqtt = mqtt_client.Client(mqtt_client_id, transport=self.transport)
        mqtt.username_pw_set(mqtt_user, mqtt_passwd)
        if not self.domain_direct or self.tls:
            mqtt.tls_set(ca_certs=self.ca_certs)

        return mqtt

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

        content = "clientId" + self.client_id + "deviceName" + self.device_name + "productKey" + self.product_key + "timestamp" + str(round(time.time()))
        sign = hmac.new(bytes(self.device_secret, 'utf-8'), bytes(content, 'utf-8'), hashlib.sha1).hexdigest()
        response = requests.post(HTTPS_AUTH.format(region=self.region),
                                 data={'productKey': self.product_key,
                                       'deviceName': self.device_name,
                                       'clientId': self.client_id,
                                       'signmethod': "hmacsha1",
                                       "resources": "mqtt",
                                       "timestamp": str(round(time.time())),
                                       "sign": sign}).json()
        if response['code'] != 200:
            raise ValueError("获取连接信息错误:{}".format(response))

        self.mqtt_uri = response['data']['resources']['mqtt']['host']
        self.mqtt_port = response['data']['resources']['mqtt']['port']

        return self.client_id, response['data']['iotId'], response['data']['iotToken']
