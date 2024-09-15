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


def is_valid_ipv4(ip_str):
    parts = ip_str.split(".")

    # IPv4 地址应该有 4 个部分
    if len(parts) != 4:
        return False

    for part in parts:
        # 每个部分应该是数字，且范围在 0 到 255 之间
        if not part.isdigit() or not 0 <= int(part) <= 255:
            return False

        # 防止 '01' 这种非法的情况
        if part != str(int(part)):
            return False

    return True


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
    headers = {
        "User-Agent": "curl/7.88.1"
    }
    urls = [
        "https://ipv4.ip.sb",
        "https://ip.ping0.cc",
        "https://ipv4.ifconfig.me",
        "https://ipv4.icanhazip.com"
    ]

    connector = ProxyConnector.from_url(proxy_str)

    url = random.choice(urls)
    timeout = aiohttp.ClientTimeout(total=5)

    try:
        async with aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
        ) as session, session.get(url, headers=headers, ssl=False) as resp:
            ip = await resp.text()
            ip = ip.strip()
            logger.info(f'proxy: {proxy_str} use {url} get outbound_ip: {ip}')
            if is_valid_ipv4(ip):
                return ip
    except Exception as e:
        logger.error(f'proxy: {proxy_str} use {url} get ip error: {e}')

    return ''


if __name__ == '__main__':
    import requests

    # for _ in range(100):
    # proxy = requests.get('http://192.168.50.88:5010/get?type=http').json().get('proxy')
    proxy = 'socks5://3.123.150.192:3128'
    logger.info(f"proxy: {proxy}")
    ret = asyncio.run(check(proxy))
    print(ret)
