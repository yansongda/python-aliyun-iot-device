# -*- coding: utf-8 -*-

from aliyun_iot_device.mqtt import Client
import time

PRODUCE_KEY = "b1VzFx30hEm"
DEVICE_NAME = "iot_device_01"
DEVICE_SECRET = "3TSqd6sfzjSkSwEmLmcAdZnI0oGlmRZ8"
CLIENT_ID = ""

PUBLISH_TOPIC = "/" + PRODUCE_KEY + "/" + DEVICE_NAME + "/update"
SUBSCRIBE_TOPIC = "/" + PRODUCE_KEY + "/" + DEVICE_NAME + "/get"

iot = Client(("b1VzFx30hEm", "iot_device_01", "3TSqd6sfzjSkSwEmLmcAdZnI0oGlmRZ8"), "yansongda")
iot.tls = False

iot.connect()

iot.mqtt.loop_start()
while True:
    iot.mqtt.publish(PUBLISH_TOPIC, 'success', 1)
    time.sleep(5)
