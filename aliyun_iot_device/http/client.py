# -*- coding: utf-8 -*-

__author__ = "yansongda <me@yansongda.cn>"

from cachetools import TTLCache
import requests
import hashlib
import json
import hmac

HTTP_URI = "https://iot-as-http.{region}.aliyuncs.com/{uri}"

DEFAULT_PUBLISH_TOPIC = "/{product_key}/{device_name}/update"
DEFAULT_SUBSCRIBE_TOPIC = "/{product_key}/{device_name}/get"

SHADOW_UPDATE_TOPIC = "/shadow/update/{product_key}/{device_name}"
SHADOW_GET_TOPIC = "/shadow/get/{product_key}/{device_name}"


class Client(object):
    """阿里云 IOT 物联网套件 HTTP 客户端
    """

    def __init__(self, product_device, client_id=None, region="cn-shanghai"):
        """product_device: (tuple) 阿里云规定三元组，分别为 PRODUCE_KEY, DEVICE_NAME, DEVICE_SECRET

        client_id: (None, str) 客户端 id，如果为 None 或者 ""，则 SDK 自动设置为 DEVICE_NAME

        region: (str) 阿里云地域，目前有cn-shanghai，us-west-1，ap-southeast-1
        """
        super(Client, self).__init__()
        if not isinstance(product_device, tuple):
            raise TypeError('{pd} Must Be A Tuple'.format(pd=product_device))

        if client_id is None or client_id == "":
            client_id = product_device[1]

        self.client_id = client_id
        self.region = region
        self.product_key, self.device_name, self.device_secret = product_device
        self.cache = TTLCache(maxsize=1, ttl=48 * 60 * 60)

    def publish(self, payload=None, topic=None, token=None):
        """payload: (str/int/float/None) 负载

        topic: (string) 发布的主题，默认为阿里云默认主题，即："/{product_key}/{device_name}/update"

        token: 发布时所携带的 token，如果为 None，则 SDK 自动缓存获取
        """
        if topic is None:
            topic = DEFAULT_PUBLISH_TOPIC.format(product_key=self.product_key, device_name=self.device_name)
        if topic == 'shadow':
            topic = SHADOW_UPDATE_TOPIC.format(product_key=self.product_key, device_name=self.device_name)

            data = {"method": payload['method']}
            if 'reported' in payload:
                data.update({"state": {"reported": payload['reported']}})
            if 'version' in payload:
                data.update({"version": payload['version']})
            payload = json.dumps(data)

        if token is None:
            token = self.get_token()

        response = self._request_api(uri='topic' + topic, data=bytes(payload, 'utf-8'),
                                     headers={"password": token, "Content-Type": "application/octet-stream"})

        return response

    def get_token(self, cache=True):
        """获取 token

        cache: 如果为 True，则使用缓存。默认使用内存型缓存 cachetools 方案
        """
        if cache:
            try:
                return self.cache['token']
            except KeyError:
                self.cache['token'] = self._request_api(uri='auth')['token']
            return self.cache['token']

        return self._request_api(uri='auth')['token']

    def _request_api(self, uri, data=None, headers=None):
        """与阿里云服务器通讯
        """
        if data is None:
            data = json.dumps({"productKey": self.product_key,
                               "deviceName": self.device_name,
                               "clientId": self.client_id,
                               "signmethod": "hmacsha1",
                               "version": "default",
                               "sign": self._get_sign()})
        if headers is None:
            headers = {"Content-Type": "application/json"}

        response = requests.post(HTTP_URI.format(region=self.region, uri=uri),
                                 data=data, headers=headers).json()
        if response['code'] != 0:
            raise ValueError("与阿里云通讯出错，uri:{uri}，response:{response}".format(uri=uri, response=response))

        return response['info']

    def _get_sign(self):
        """获取签名
        """
        content = "clientId" + self.client_id + "deviceName" + self.device_name + "productKey" + self.product_key
        return hmac.new(bytes(self.device_secret, 'utf-8'), bytes(content, 'utf-8'), hashlib.sha1).hexdigest()
