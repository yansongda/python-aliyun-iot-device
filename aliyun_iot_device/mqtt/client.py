# -*- coding: utf-8 -*-

__author__ = "yansongda <me@yansongda.cn>"

import paho.mqtt.client as mqtt_client
import hashlib
import hmac
import time
import os

DOMAIN_DIRECT_URI = "{product_key}.iot-as-mqtt.{region}.aliyuncs.com"
DOMAIN_DIRECT_PORT = 1883

HTTPS_AUTH = "https://iot-auth.{region}.aliyuncs.com/auth/devicename"

DEFAULT_PUBLISH_TOPIC = "/{product_key}/{device_name}/update"
DEFAULT_SUBSCRIBE_TOPIC = "/{product_key}/{device_name}/get"

KEEPALIVE = 60


class Client(object):
    """阿里云 IOT 套件 MQTT 客户端
    """

    def __init__(self, product_device, client_id=None, region="cn-shanghai", domain_direct=True, ca_certs=None):
        super(Client, self).__init__()
        if not isinstance(product_device, tuple):
            raise TypeError('{pd} Must Be A Tuple'.format(pd=product_device))

        self.client_id = client_id
        self.region = region
        self.ca_certs = ca_certs
        self.domain_direct = domain_direct
        self.product_key, self.device_name, self.device_secret = product_device

        self.mqtt_uri = DOMAIN_DIRECT_URI.format(product_key=self.product_key, region=region)
        self.mqtt_port = DOMAIN_DIRECT_PORT
        self.mqtt = self.get_mqtt_client()

    def connect(self, keepalive=KEEPALIVE):
        return self.mqtt.connect(self.mqtt_uri, self.mqtt_port, keepalive)

    def get_mqtt_client(self):
        if self.domain_direct:
            mqtt_client_id, mqtt_user, mqtt_passwd = self._get_doamin_direct_mqtt_info()
        else:
            mqtt_client_id, mqtt_user, mqtt_passwd = self._get_https_mqtt_info()

        mqtt = mqtt_client.Client(mqtt_client_id)
        mqtt.username_pw_set(mqtt_user, mqtt_passwd)
        if self.ca_certs:
            mqtt.tls_set(ca_certs=self.ca_certs)

        return mqtt

    def _get_doamin_direct_mqtt_info(self):
        mode = "3"
        if self.ca_certs:
            mode = "2"

        mqtt_client_id = self.client_id + "|securemode=" + mode + ",signmethod=hmacsha1,timestamp=" + str(round(time.time())) + "|"
        mqtt_user = self.device_name + "&" + self.product_key
        mqtt_content = "clientId" + self.client_id + "deviceName" + self.device_name + "productKey" + self.product_key + "timestamp" + str(round(time.time()))
        mqtt_passwd = hmac.new(bytes(self.device_secret, 'utf-8'), bytes(mqtt_content, 'utf-8'), hashlib.sha1).hexdigest()

        return mqtt_client_id, mqtt_user, mqtt_passwd

    def _get_https_mqtt_info(self):
        pass
