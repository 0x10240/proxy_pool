import asyncio
import aiohttp
import random

from aiohttp_socks import ProxyConnector
from loguru import logger

HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
    'Accept': '*/*',
    'Connection': 'keep-alive',
    'Accept-Language': 'zh-CN,zh;q=0.8'
}

async def httpsTimeOutValidator(proxy):
    """HTTPS detection with timeout using aiohttp"""
    try:
        timeout = aiohttp.ClientTimeout(total=3)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.head("http://httpbin.org", headers=HEADER, proxy=proxy, ssl=False) as resp:
                return resp.status == 200
    except Exception:
        return False

async def check(proxy_str):
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://ipv4.ping0.cc", headers=HEADER, proxy=proxy_str, ssl=False) as resp:
                if resp.status == 200:
                    print(await resp.text())
    except Exception:
        return False



if __name__ == '__main__':
    import requests
    for _ in range(100):
        proxy = requests.get('http://192.168.50.88:5010/get?type=http').json().get('proxy')
        # proxy = 'http://113.240.99.148:65007'
        logger.info(f"proxy: {proxy}")
        ret = asyncio.run(check(proxy))
        print(ret)
