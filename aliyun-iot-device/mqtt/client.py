# -*- coding: utf-8 -*-

__author__ = "yansongda <me@yansongda.cn>"

import paho.mqtt.client as mqtt
import hashlib
import hmac
import time

URI = "aliyuncs.com"


class Client(object):
    """阿里云 IOT 套件 MQTT 客户端
    """

    # 是否使用 TLS 加密
    tls = True

    # 是否使用域名直连
    direct = True

    def __init__(self, product_key, device_name, device_secret, client_id=None, region="cn-shanghai"):
        super(Client, self).__init__()
        self.client_id = client_id
        self.product_key = product_key
        self.device_name = device_name
        self.device_secret = device_secret
        self.region = region

    def connect(self):
        pass

    @property
    def tls(self):
        return self.tls

    @tls.setter
    def tls(self, value):
        if isinstance(value, bool):
            self.tls = value

        raise ValueError("{0} must be bool".format(value))

    @property
    def direct(self):
        return self.direct

    @direct.setter
    def direct(self, value):
        if isinstance(value, bool):
            self.direct = value

        raise ValueError("{0} must be bool".format(value))
