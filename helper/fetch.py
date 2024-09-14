# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     fetchScheduler
   Description :
   Author :        JHao
   date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2021/11/18: 多线程采集
-------------------------------------------------
"""
__author__ = 'JHao'

from threading import Thread
from helper.proxy import Proxy
from helper.check import DoValidator
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from fetcher.proxyFetcher import ProxyFetcher
from handler.configHandler import ConfigHandler
from loguru import logger


class _ThreadFetcher(Thread):

    def __init__(self, fetch_source, proxy_dict):
        Thread.__init__(self)
        self.fetch_source = fetch_source
        self.proxy_dict = proxy_dict
        self.fetcher = getattr(ProxyFetcher, fetch_source, None)
        self.log = LogHandler("fetcher")
        self.conf = ConfigHandler()
        self.proxy_handler = ProxyHandler()

    def run(self):
        logger.info("ProxyFetch - {func}: start".format(func=self.fetch_source))
        try:
            for proxy in self.fetcher():
                type, ip, port, source = proxy.get('type'), proxy.get('ip'), proxy.get('port'), proxy.get('source')
                proxy_str = f"{type}://{ip}:{port}"

                logger.info('ProxyFetch - %s: %s ok' % (self.fetch_source, proxy_str.ljust(30)))

                if proxy_str in self.proxy_dict:
                    self.proxy_dict[proxy_str].add_source(source)
                else:
                    self.proxy_dict[proxy_str] = Proxy(proxy_str, source=source)
        except Exception as e:
            logger.exception(f"ProxyFetch - {self.fetch_source}: error: {e}")


class Fetcher(object):
    name = "fetcher"

    def __init__(self):
        self.log = LogHandler(self.name)
        self.conf = ConfigHandler()

    def run(self):
        """
        fetch proxy with proxyFetcher
        :return:
        """
        proxy_dict = dict()
        thread_list = list()
        logger.info("ProxyFetch : start")

        for fetch_source in self.conf.fetchers:
            logger.info("ProxyFetch - {func}: start".format(func=fetch_source))
            fetcher = getattr(ProxyFetcher, fetch_source, None)
            if not fetcher:
                logger.error("ProxyFetch - {func}: class method not exists!".format(func=fetch_source))
                continue
            if not callable(fetcher):
                logger.error("ProxyFetch - {func}: must be class method".format(func=fetch_source))
                continue
            thread_list.append(_ThreadFetcher(fetch_source, proxy_dict))

        for thread in thread_list:
            thread.setDaemon(True)
            thread.start()

        for thread in thread_list:
            thread.join()

        logger.info("ProxyFetch - all complete!")
        for item in proxy_dict.values():
            if DoValidator.preValidator(item.proxy):
                yield item
