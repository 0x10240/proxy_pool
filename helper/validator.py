# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     validator.py
   Description :   Define proxy validation methods using aiohttp
   Author :        JHao
   Date：          2021/5/25
-------------------------------------------------
   Change Activity:
                   2023/03/10: Support proxies with user authentication username:password@ip:port
                   2023/09/14: Rewrite using aiohttp and asynchronous programming
-------------------------------------------------
"""

import re

import aiohttp
import asyncio

from util.six import withMetaclass
from util.singleton import Singleton
from handler.configHandler import ConfigHandler
from aiohttp_socks import ProxyConnector

conf = ConfigHandler()

HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
    'Accept': '*/*',
    'Connection': 'keep-alive',
    'Accept-Language': 'zh-CN,zh;q=0.8'
}

IP_REGEX = re.compile(r".*://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}")


class ProxyValidator(withMetaclass(Singleton)):
    pre_validator = []
    http_validator = []
    https_validator = []
    socks_validator = []

    @classmethod
    def addPreValidator(cls, func):
        cls.pre_validator.append(func)
        return func

    @classmethod
    def addHttpValidator(cls, func):
        cls.http_validator.append(func)
        return func

    @classmethod
    def addHttpsValidator(cls, func):
        cls.https_validator.append(func)
        return func

    @classmethod
    def addSocksValidator(cls, func):
        cls.socks_validator.append(func)
        return func


@ProxyValidator.addPreValidator
async def formatValidator(proxy):
    """Check proxy format"""
    return True if IP_REGEX.fullmatch(proxy) else False


@ProxyValidator.addHttpValidator
async def httpTimeOutValidator(proxy):
    """HTTP detection with timeout using aiohttp"""
    try:
        timeout = aiohttp.ClientTimeout(total=conf.verifyTimeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.head(conf.httpUrl, headers=HEADER, proxy=proxy) as resp:
                return resp.status == 200
    except Exception:
        return False


@ProxyValidator.addHttpsValidator
async def httpsTimeOutValidator(proxy):
    """HTTPS detection with timeout using aiohttp"""
    try:
        timeout = aiohttp.ClientTimeout(total=conf.verifyTimeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.head(conf.httpsUrl, headers=HEADER, proxy=proxy, ssl=False) as resp:
                return resp.status == 200
    except Exception:
        return False


@ProxyValidator.addSocksValidator
async def socksTimeOutValidator(proxy):
    """SOCKS detection with timeout using aiohttp"""
    # Note: For SOCKS proxies, you need to install aiohttp_socks
    try:
        timeout = aiohttp.ClientTimeout(total=conf.verifyTimeout)
        connector = ProxyConnector.from_url(proxy)
        async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
        ) as session, session.get(conf.httpsUrl, headers=HEADER, ssl=False) as resp:
            return resp.status == 200
    except Exception as e:
        # logger.exception(f'socksTimeOutValidator error: {e}')
        return False


@ProxyValidator.addHttpValidator
async def customValidatorExample(proxy):
    """Custom validator function, check if the proxy is available, return True/False"""
    # Implement your custom validation logic here
    return True


async def test():
    import requests

    data = requests.get("http://192.168.50.88:5010//all/?valid=true&type=socks5").json()
    proxies = [x.get('proxy') for x in data]
    tasks = []

    async with aiohttp.ClientSession() as session:
        for proxy in proxies:
            p = ProxyValidator()
            for func in p.socks_validator:
                task = asyncio.create_task(func(proxy))  # 使用 create_task 提交任务
                tasks.append(task)

    res = await asyncio.gather(*tasks)
    for i in range(len(proxies)):
        proxy = proxies[i]
        resi = res[i]
        print(proxy, resi)


if __name__ == '__main__':
    asyncio.run(test())
