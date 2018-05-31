# -*- coding: utf-8 -*-

__author__ = "yansongda <me@yansongda.cn>"

import requests
import hashlib
import hmac

HTTP_URI = "https://iot-as-http.{region}.aliyuncs.com"

DEFAULT_PUBLISH_TOPIC = "/{product_key}/{device_name}/update"
DEFAULT_SUBSCRIBE_TOPIC = "/{product_key}/{device_name}/get"


class Client(object):
    """docstring for Client"""

    def __init__(self, product_device, client_id=None, region="cn-shanghai"):
        super(Client, self).__init__()
        self.client_id = client_id
        self.region = region
        self.product_key, self.device_name, self.device_secret = product_device

    def get_token(self):
        pass

    def publish(self, payload=None, topic=None):
        if topic is None:
            topic = DEFAULT_PUBLISH_TOPIC.format(product_key=self.product_key, device_name=self.device_name)
