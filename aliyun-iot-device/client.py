# -*- coding: utf-8 -*-

__author__ = "yansongda <me@yansongda.cn>"

import paho.mqtt.client as mqtt
import hashlib
import hmac
import time


class Client(mqtt.Client):
    """docstring for Client"""

    def __init__(self, clientId):
        super(Client, self).__init__()
        self.arg = arg
