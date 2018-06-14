# -*- coding: utf-8 -*-

__author__ = "yansongda <me@yansongda.cn>"

import context
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
