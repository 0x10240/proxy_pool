# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyFetcher
   Description :
   Author :        JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: proxyFetcher
-------------------------------------------------
"""
__author__ = 'JHao'

import base64
import re
import json
import asyncio

from util.webRequest import WebRequest
from loguru import logger
from setting import FETCHER_COMMON_SOURCE


class ProxyFetcher(object):
    """
    proxy getter
    """

    @staticmethod
    async def common():
        semaphore = asyncio.Semaphore(10)  # 限制并发数为
        results = dict()
        lock = asyncio.Lock()  # 创建锁

        async def fetch_source(source_info):
            url = source_info['url']
            proxy_type = source_info['type']
            source = source_info['source']

            async with semaphore:  # 信号量限制
                try:
                    status, text = await WebRequest().get(url=url)
                    if status == 200 and text:
                        regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}"
                        proxies = re.findall(regex, text)

                        async with lock:  # 使用锁来保护 results 的修改
                            logger.info(f'proxies from: {source}, {proxy_type} count: {len(proxies)}')
                            for proxy in proxies:
                                if isinstance(proxy, str) and proxy.count(':') == 1:
                                    ip, port = proxy.split(':')
                                    results[proxy] = {
                                        'type': proxy_type,
                                        'ip': ip,
                                        'port': port,
                                        'source': source
                                    }
                except Exception as e:
                    logger.exception(f'url: {url}, type: {proxy_type}, source: {source} Fetch error: {e}')

        tasks = [fetch_source(source_info) for source_info in FETCHER_COMMON_SOURCE]
        await asyncio.gather(*tasks)

        values = results.values()
        logger.info(f'common proxies count: {len(values)}')
        for v in values:
            yield v

    @staticmethod
    async def geonode(self):
        semaphore = asyncio.Semaphore(3)  # 限制并发数为 10
        results = dict()
        lock = asyncio.Lock()  # 创建锁

        async def fetch_page_data(page):
            url = f"https://proxylist.geonode.com/api/proxy-list?protocols=socks5&limit=500&page={page}&sort_by=lastChecked&sort_type=desc"
            async with semaphore:  # 信号量限制
                try:
                    status, text = await WebRequest().get(url=url)
                    if status == 200 and text:
                        data = json.loads(text).get('data', [])

                        async with lock:
                            for item in data:
                                if item.get('ip') == '127.0.0.1':
                                    continue
                                results[item.get('_id', '')] = {
                                    'type': 'socks5',
                                    'ip': item.get('ip'),
                                    'port': item.get('port'),
                                    'source': 'geonode'
                                }
                except Exception as e:
                    logger.error(f'geonode page: {page} url: {url}, error: {e}')

        tasks = [fetch_page_data(page) for page in range(1, 4)]
        await asyncio.gather(*tasks)

        values = results.values()
        logger.info(f'geonode proxies count: {len(values)}')
        for v in values:
            yield v

    @staticmethod
    async def lumiproxy():
        url = "https://api.lumiproxy.com/web_v1/free-proxy/list?page_size=1000&page=1&protocol=8&language=zh-hans"
        try:
            status, text = await WebRequest().get(url=url)
            if status == 200 and text:
                proxies = json.loads(text).get('data', {}).get('list', [])
                logger.info(f'lumi proxies count: {len(proxies)}')
                for proxy in proxies:
                    yield {
                        'source': 'lumiproxy',
                        'type': 'socks5',
                        'ip': proxy['ip'],
                        'port': proxy['port']
                    }
        except Exception as e:
            logger.error(f'geonode url: {url}, error: {e}')

    @staticmethod
    async def free_proxy_list_net():
        url = f"https://free-proxy-list.net/#"
        try:
            status, text = await WebRequest().get(url=url)
            if status == 200 and text:
                proxies = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)', text)
                for proxy in proxies:
                    ip, port = proxy
                    yield {
                        'type': 'http',
                        'ip': ip,
                        'port': port,
                        'source': 'free-proxy-list'
                    }
        except Exception as e:
            logger.error(f'geonode url: {url}, error: {e}')

    @staticmethod
    async def advanced_name():
        semaphore = asyncio.Semaphore(3)  # 限制并发数为
        results = dict()
        lock = asyncio.Lock()  # 创建锁

        async def fetch_page_data(page):
            url = f"https://advanced.name/freeproxy?page={page}"
            async with semaphore:  # 信号量限制
                try:
                    status, text = await WebRequest().get(url=url)
                    if status == 200 and text:
                        trs = re.findall(r'<tr>.*?</tr>', text, re.S)
                        async with lock:
                            for tr in trs:
                                try:
                                    if 'socks5' not in tr.lower():
                                        continue

                                    ip_b64 = re.search('<td data-ip="(.*?)"></td>', tr).group(1)
                                    port_b64 = re.search('<td data-port="(.*?)"></td>', tr).group(1)
                                    ip = base64.b64decode(ip_b64).decode('utf-8')
                                    port = base64.b64decode(port_b64).decode('utf-8')

                                    type = 'socks5'
                                    results[f'{ip}:{port}'] = {
                                        'type': type,
                                        'ip': ip,
                                        'port': port,
                                        'source': 'advanced.name'
                                    }
                                except Exception:
                                    continue
                except Exception as e:
                    logger.error(f'geonode page: {page} url: {url}, error: {e}')

        tasks = [fetch_page_data(page) for page in range(1, 5)]
        await asyncio.gather(*tasks)

        values = results.values()
        logger.info(f'geonode proxies count: {len(values)}')
        for v in values:
            yield v


if __name__ == '__main__':
    p = ProxyFetcher()

    async def run():
        async for proxy_data in p.common():
            print(proxy_data)
            pass

    asyncio.run(run())
