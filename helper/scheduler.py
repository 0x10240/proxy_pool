# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyScheduler
   Description :   Schedule proxy fetching and checking using asyncio
   Author :        JHao
   Date：          2019/8/5
-------------------------------------------------
   Change Activity:
                   2019/08/05: proxyScheduler
                   2021/02/23: Run fetch when remaining proxies are fewer than POOL_SIZE_MIN during runProxyCheck
                   2023/09/14: Adapted to use asynchronous versions of validator and checker
                   2023/09/14: Modified to run fetch and check immediately at startup
-------------------------------------------------
"""
__author__ = 'JHao'

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from helper.fetch import Fetcher
from helper.check import Checker
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler


async def __runProxyFetch():
    proxy_queue = asyncio.Queue()
    proxy_fetcher = Fetcher()

    # Assuming Fetcher.run() is now asynchronous
    async for proxy in proxy_fetcher.run():
        await proxy_queue.put(proxy)

    await Checker("raw", proxy_queue)


async def __runProxyCheck():
    proxy_handler = ProxyHandler()
    proxy_queue = asyncio.Queue()
    conf = ConfigHandler()

    count = await proxy_handler.db.getCount()
    if count.get("total", 0) < conf.poolSizeMin:
        await __runProxyFetch()
    proxies = await proxy_handler.getAll()
    for proxy in proxies:
        await proxy_queue.put(proxy)
    await Checker("use", proxy_queue)


async def main():
    timezone = ConfigHandler().timezone
    scheduler_log = LogHandler("scheduler")
    job_defaults = {
        'coalesce': False,
        'max_instances': 10
    }

    # Initialize the AsyncIOScheduler without specifying executors
    scheduler = AsyncIOScheduler(logger=scheduler_log, timezone=timezone, job_defaults=job_defaults)

    # Add jobs to the scheduler
    scheduler.add_job(__runProxyFetch, 'interval', minutes=10, id="proxy_fetch", name="Proxy Fetch")
    scheduler.add_job(__runProxyCheck, 'interval', minutes=3, id="proxy_check", name="Proxy Check")

    # Start the scheduler
    scheduler.start()

    # Run the functions immediately
    await __runProxyFetch()
    await __runProxyCheck()

    try:
        # Keep the event loop running
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
