# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     fetch.py
   Description :   Asynchronous proxy fetching
   Author :        JHao
   Date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2021/11/18: Multi-threaded fetching
                   2023/09/14: Adapted to use asynchronous fetching with asyncio
-------------------------------------------------
"""
__author__ = 'JHao'

import asyncio
from helper.proxy import Proxy
from helper.check import DoValidator
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from fetcher.proxyFetcher import ProxyFetcher
from handler.configHandler import ConfigHandler
from loguru import logger


class Fetcher:
    name = "fetcher"

    def __init__(self):
        self.log = LogHandler(self.name)
        self.conf = ConfigHandler()
        self.proxy_handler = ProxyHandler()

    async def run(self):
        """
        Fetch proxies asynchronously
        """
        proxy_dict = dict()
        logger.info("ProxyFetch : start")

        tasks = []
        for fetch_source in self.conf.fetchers:
            logger.info(f"ProxyFetch - {fetch_source}: start")
            fetcher = getattr(ProxyFetcher, fetch_source, None)
            if not fetcher:
                logger.error(f"ProxyFetch - {fetch_source}: method not exists!")
                continue
            if not callable(fetcher):
                logger.error(f"ProxyFetch - {fetch_source}: must be callable")
                continue

            # Create a task for the fetcher
            task = asyncio.create_task(self._fetch_proxies(fetch_source, fetcher, proxy_dict))
            tasks.append(task)

        # Wait for all fetcher tasks to complete
        await asyncio.gather(*tasks)

        logger.info("ProxyFetch - all complete!")
        for item in proxy_dict.values():
            if await DoValidator.preValidator(item.proxy):
                yield item

    async def _fetch_proxies(self, fetch_source, fetcher, proxy_dict):
        logger.info(f"ProxyFetch - {fetch_source}: fetching proxies")
        try:
            async for proxy_data in fetcher():
                # Process proxy_data
                proxy_type = proxy_data.get('type')
                ip = proxy_data.get('ip')
                port = proxy_data.get('port')
                source = proxy_data.get('source')
                proxy_str = f"{proxy_type}://{ip}:{port}"

                logger.info(f'ProxyFetch - {source}: {proxy_str.ljust(30)} ok')

                if proxy_str in proxy_dict:
                    proxy_dict[proxy_str].add_source(source)
                else:
                    proxy_dict[proxy_str] = Proxy(proxy_str, source=source)
        except Exception as e:
            logger.exception(f"ProxyFetch - {fetch_source}: error: {e}")
