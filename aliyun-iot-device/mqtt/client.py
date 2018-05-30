# -*- coding: utf-8 -*-

__author__ = "yansongda <me@yansongda.cn>"

import paho.mqtt.client as mqtt_client
import hashlib
import hmac
import time

DOMAIN_DIRECT_URI = "{product_key}.iot-as-mqtt.{region}.aliyuncs.com"
DOMAIN_DIRECT_PORT = 1883

HTTPS_AUTH = "https://iot-auth.{region}.aliyuncs.com/auth/devicename"

DEFAULT_PUBLISH_TOPIC = "/{product_key}/{device_name}/update"
DEFAULT_SUBSCRIBE_TOPIC = "/{product_key}/{device_name}/get"

KEEPALIVE = 60


class Client(object):
    """阿里云 IOT 套件 MQTT 客户端
    """

    # 是否使用 TLS 加密
    tls = True

    # 是否使用域名直连
    domain_direct = True

    mqtt_uri = DOMAIN_DIRECT_URI

    mqtt_port = DOMAIN_DIRECT_PORT

    def __init__(self, product_device, client_id=None, region="cn-shanghai"):
        super(Client, self).__init__()
        if not isinstance(product_device, tuple):
            raise TypeError('{pd} Must Be A Tuple'.format(pd=product_device))

        self.client_id = client_id
        self.region = region
        self.product_key, self.device_name, self.device_secret = product_device
        self.mqtt = self.get_mqtt_client()

    def connect(self, keepalive=KEEPALIVE):
        return self.mqtt.connect(self.mqtt_uri, self.mqtt_port, keepalive)

    def get_mqtt_client(self):
        if self.domain_direct:
            mqtt_client_id, mqtt_user, mqtt_passwd = self._get_doamin_direct_mqtt_info()
        else:
            mqtt_client_id, mqtt_user, mqtt_passwd = self._get_https_mqtt_info()

        mqtt = mqtt_client(mqtt_client_id)
        mqtt.tls_set(ca_certs="root.cer")
        mqtt.username_pw_set(mqtt_user, mqtt_passwd)

        return mqtt

    @tls.setter
    def tls(self, value):
        if isinstance(value, bool):
            self.tls = value

        raise ValueError("{0} Must Be Bool".format(value))

    @domain_direct.setter
    def domain_direct(self, value):
        if isinstance(value, bool):
            self.domain_direct = value

        raise ValueError("{0} must be bool".format(value))

    def _get_doamin_direct_mqtt_info(self):
        mode = 3
        if self.tls:
            mode = 2

        mqtt_client_id = self.client_id + "|securemode=" + mode + ",signmethod=hmacsha1,timestamp=" + str(round(time.time())) + "|"
        mqtt_user = self.device_name + "&" + self.product_key
        mqtt_content = "clientId" + self.client_id + "deviceName" + self.device_name + "productKey" + self.product_key + "timestamp" + str(round(time.time()))
        mqtt_passwd = hmac.new(bytes(self.device_secret, 'utf-8'), bytes(mqtt_content, 'utf-8'), hashlib.sha1).hexdigest()

        return mqtt_client_id, mqtt_user, mqtt_passwd

    def _get_https_mqtt_info(self):
        pass
