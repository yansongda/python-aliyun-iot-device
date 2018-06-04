# -*- coding: utf-8 -*-

__author__ = "yansongda <me@yansongda.cn>"

import context
from aliyun_iot_device.http import Client as IOT
import time

PRODUCE_KEY = "b1VzFx30hEm"
DEVICE_NAME = "iot_device_01"
DEVICE_SECRET = "3TSqd6sfzjSkSwEmLmcAdZnI0oGlmRZ8"

iot = IOT((PRODUCE_KEY, DEVICE_NAME, DEVICE_SECRET))

while True:
    iot.publish('success')
    time.sleep(5)
