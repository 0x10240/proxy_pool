# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     Proxy
   Description :   代理对象类型封装
   Author :        JHao
   date：          2019/7/11
-------------------------------------------------
   Change Activity:
                   2019/7/11: 代理对象类型封装
-------------------------------------------------
"""
__author__ = 'JHao'

import json
from loguru import logger


class Proxy(object):

    def __init__(self, proxy, fail_count=0, region="", anonymous="",
                 source="", check_count=0, last_status="", last_time="", https=False, outbound_ip=''):
        self._proxy = proxy
        self.type, self.ip, self.port = proxy.split(":")
        self.ip = self.ip.replace("//", "")
        self._fail_count = fail_count
        self._region = region
        self._anonymous = anonymous
        self._source = source.split('/')
        self._check_count = check_count
        self._last_status = last_status
        self._last_time = last_time
        self._https = https
        self.outbound_ip = ""

    @classmethod
    def createFromJson(cls, data):
        return cls(
            proxy=data.get("proxy", ""),
            fail_count=data.get("fail_count", 0),
            anonymous=data.get("anonymous", ""),
            source=data.get("source", ""),
            check_count=data.get("check_count", 0),
            last_status=data.get("last_status", ""),
            last_time=data.get("last_time", ""),
            https=data.get("https", False),
            outbound_ip=data.get("outbound_ip", "")
        )

    @property
    def proxy(self):
        """ 代理 ip:port """
        return self._proxy

    @property
    def fail_count(self):
        """ 检测失败次数 """
        return self._fail_count

    @property
    def region(self):
        """ 地理位置(国家/城市) """
        return self._region

    @property
    def anonymous(self):
        """ 匿名 """
        return self._anonymous

    @property
    def source(self):
        """ 代理来源 """
        return '/'.join(self._source)

    @property
    def check_count(self):
        """ 代理检测次数 """
        return self._check_count

    @property
    def last_status(self):
        """ 最后一次检测结果  True -> 可用; False -> 不可用"""
        return self._last_status

    @property
    def last_time(self):
        """ 最后一次检测时间 """
        return self._last_time

    @property
    def https(self):
        """ 是否支持https """
        return self._https

    @property
    def to_dict(self):
        """ 属性字典 """
        return {
            "proxy": self.proxy,
            "https": self.https,
            "type": self.type,
            "ip": self.ip,
            "port": self.port,
            "outbound_ip": self.outbound_ip,
            "fail_count": self.fail_count,
            "region": self._region,
            "anonymous": self.anonymous,
            "source": self.source,
            "check_count": self.check_count,
            "last_status": self.last_status,
            "last_time": self.last_time
        }

    @property
    def to_json(self):
        """ 属性json格式 """
        try:
            return json.dumps(self.to_dict, ensure_ascii=False)
        except Exception as e:
            logger.exception(e)
            return {}

    @fail_count.setter
    def fail_count(self, value):
        self._fail_count = value

    @check_count.setter
    def check_count(self, value):
        self._check_count = value

    @last_status.setter
    def last_status(self, value):
        self._last_status = value

    @last_time.setter
    def last_time(self, value):
        self._last_time = value

    @https.setter
    def https(self, value):
        self._https = value

    @region.setter
    def region(self, value):
        self._region = value

    def add_source(self, source_str):
        if source_str:
            self._source.append(source_str)
            self._source = list(set(self._source))


if __name__ == '__main__':
    p = Proxy('::')
    p.region = "1234"
    print(p.to_json)
