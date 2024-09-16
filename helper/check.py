# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     check.py
   Description :   Execute proxy validation using aiohttp and asyncio
   Author :        JHao
   Date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2019/08/06: Execute proxy validation
                   2021/05/25: Validate HTTP and HTTPS separately
                   2022/08/16: Get proxy region information
                   2023/09/14: Rewrite using aiohttp and asynchronous programming
-------------------------------------------------
"""

import asyncio
import aiohttp
import random

from datetime import datetime
from util.webRequest import WebRequest
from handler.logHandler import LogHandler
from helper.validator import ProxyValidator
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler
from aiohttp_socks import ProxyConnector
from helper.geoip import get_geo_info
from loguru import logger


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


async def get_outbound_ip(proxy_str):
    headers = {
        "User-Agent": "curl/7.88.1"
    }
    urls = [
        "http://ipv4.ip.sb",
        "http://ip.ping0.cc",
        "http://ipv4.ifconfig.me",
        "http://ipv4.icanhazip.com",
        "http://158.180.69.99:8080/",
        "http://5.45.99.39:38080/"
    ]

    proxy, connector = None, None
    if proxy_str.startswith("http"):
        proxy = proxy_str
    elif proxy_str.startswith("socks"):
        connector = ProxyConnector.from_url(proxy_str)

    url = random.choice(urls)
    timeout = aiohttp.ClientTimeout(total=5)

    try:
        async with aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
        ) as session, session.get(url, headers=headers, proxy=proxy, ssl=False) as resp:
            ip = await resp.text()
            ip = ip.strip()
            logger.info(f'proxy: {proxy_str} use {url} get outbound_ip: {ip}')
            if is_valid_ipv4(ip):
                return ip
    except Exception as e:
        logger.error(f'proxy: {proxy_str} use {url} get ip error: {e}')

    return ''


class DoValidator(object):
    """Perform validation"""

    conf = ConfigHandler()

    @classmethod
    async def validator(cls, proxy, work_type):
        """
        Validation entry point
        Args:
            proxy: Proxy Object
            work_type: raw/use
        Returns:
            Proxy Object
        """
        status = None

        https_support = False
        if proxy.proxy.startswith('http'):
            status = await cls.httpValidator(proxy)
            if status:
                https_support = await cls.httpsValidator(proxy)

        elif proxy.proxy.startswith('socks'):
            status = await cls.socksValidator(proxy)

        proxy.https = https_support
        proxy.check_count += 1
        proxy.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        proxy.last_status = True if status else False
        proxy.region = get_geo_info(proxy.ip)

        if status:
            if proxy.fail_count > 0:
                proxy.fail_count -= 1

            outbound_ip = await get_outbound_ip(proxy.proxy)
            proxy.outbound_ip = outbound_ip
            if outbound_ip and proxy.ip != outbound_ip:
                proxy.region = get_geo_info(outbound_ip)
        else:
            proxy.fail_count += 1
        return proxy

    @classmethod
    async def httpValidator(cls, proxy):
        for func in ProxyValidator.http_validator:
            result = await func(proxy.proxy)
            if not result:
                return False
        return True

    @classmethod
    async def httpsValidator(cls, proxy):
        for func in ProxyValidator.https_validator:
            result = await func(proxy.proxy)
            if not result:
                return False
        return True

    @classmethod
    async def socksValidator(cls, proxy):
        for func in ProxyValidator.socks_validator:
            result = await func(proxy.proxy)
            if not result:
                return False
        return True

    @classmethod
    async def preValidator(cls, proxy):
        for func in ProxyValidator.pre_validator:
            result = await func(proxy)
            if not result:
                return False
        return True

    @classmethod
    async def regionGetter(cls, proxy):
        try:
            url = 'https://searchplugin.csdn.net/api/v1/ip/get?ip=%s' % proxy.proxy.split(':')[0]
            response = await WebRequest().get(url=url, retry_time=1, timeout=2)
            data = await response.json()
            return data['data']['address']
        except:
            return 'error'


async def checker_worker(work_type, target_queue, name):
    proxy_handler = ProxyHandler()
    conf = ConfigHandler()
    log_prefix = f"{work_type.title()}ProxyCheck - {name}"
    logger.info(f"{log_prefix}: start")

    while True:
        try:
            proxy = target_queue.get_nowait()
        except asyncio.QueueEmpty:
            logger.info(f"{log_prefix}: complete")
            break

        try:
            # 校验代理
            proxy = await DoValidator.validator(proxy, work_type)

            if work_type == "raw":
                await handle_raw_proxy(proxy, proxy_handler, log_prefix)
            else:
                await handle_use_proxy(proxy, proxy_handler, conf, log_prefix)

        except Exception as e:
            logger.error(f"{log_prefix}: Error processing proxy {proxy.proxy}: {e}")

        finally:
            target_queue.task_done()


async def handle_raw_proxy(proxy, proxy_handler, log_prefix):
    if await proxy_handler.exists(proxy):
        logger.info(f'{log_prefix}: {proxy.proxy.ljust(30)} exist')
    else:
        logger.info(f'{log_prefix}: {proxy.proxy.ljust(30)} pass')
    await proxy_handler.put(proxy)


async def handle_use_proxy(proxy, proxy_handler, conf, log_prefix):
    if proxy.last_status:
        logger.info(f'{log_prefix}: {proxy.proxy.ljust(30)} pass')
        await proxy_handler.put(proxy)
        return

    if proxy.fail_count > conf.maxFailCount:
        logger.info(f'{log_prefix}: {proxy.proxy.ljust(30)} fail, count {proxy.fail_count} delete')
        await proxy_handler.delete(proxy)
    else:
        logger.info(f'{log_prefix}: {proxy.proxy.ljust(30)} fail, count {proxy.fail_count} keep')
        await proxy_handler.put(proxy)


async def Checker(tp, queue):
    """
    Run Proxy Checker
    Args:
        tp: raw/use
        queue: asyncio.Queue
    """
    tasks = []
    for index in range(50):
        task = asyncio.create_task(checker_worker(tp, queue, f"worker_{str(index).zfill(2)}"))
        tasks.append(task)
    await asyncio.gather(*tasks)
