# -*- coding: utf-8 -*-
"""
-----------------------------------------------------
   File Name：     redisClient.py
   Description :   Encapsulate Redis operations (asynchronous)
   Author :        JHao
   Date：          2019/8/9
------------------------------------------------------
   Change Activity:
                   2019/08/09: Encapsulate Redis operations
                   2020/06/23: Optimize pop method, use hscan command
                   2021/05/26: Distinguish between http/https proxies
                   2023/09/14: Adapted to use asynchronous Redis client
------------------------------------------------------
"""
__author__ = 'JHao'

import json
import redis

from random import choice
from loguru import logger

from redis.exceptions import TimeoutError, ConnectionError, ResponseError
from redis.asyncio import Redis
from redis.asyncio.connection import BlockingConnectionPool
from handler.logHandler import LogHandler


class RedisClient(object):
    """
    Asynchronous Redis client

    Proxies are stored in a Redis hash:
    Key is ip:port, value is a JSON string of proxy attributes
    """

    def __init__(self, **kwargs):
        """
        Initialize the Redis client
        :param kwargs: connection parameters (host, port, password, db, etc.)
        """
        self.name = ""
        kwargs.pop("username", None)  # Remove username if present

        # Remove 'password' key if the value is None or empty string
        # if 'password' in kwargs and not kwargs['password']:
        #     kwargs.pop('password')

        self.__conn = Redis(
            connection_pool=BlockingConnectionPool(
                decode_responses=True,
                timeout=5,
                socket_timeout=5,
                **kwargs
            )
        )

    async def get(self, type=''):
        """
        Return a proxy
        :param https: whether to return an HTTPS proxy
        :return: proxy JSON string or None
        """
        try:
            items = [json.loads(x) for x in await self.__conn.hvals(self.name)]
            items = [x for x in items if x.get("last_status") and x.get("outbound_ip")]

            if type:
                items = list(filter(lambda x: x.get("type") == type, items))

            return choice(items) if items else None
        except Exception as e:
            log = LogHandler('redis_client')
            log.error(f"Error getting proxy: {e}", exc_info=True)
            return None

    async def put(self, proxy_obj):
        """
        Put a proxy into the hash
        :param proxy_obj: Proxy object
        :return:
        """
        try:
            data = await self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)
            return data
        except Exception as e:
            logger.error(f"Error putting proxy: {e}", exc_info=True)
            return None

    async def pop(self, https):
        """
        Pop a proxy
        :param https: whether to pop an HTTPS proxy
        :return: proxy JSON string or None
        """
        proxy = await self.get(https)
        if proxy:
            await self.__conn.hdel(self.name, json.loads(proxy).get("proxy", ""))
        return proxy if proxy else None

    async def delete(self, proxy_str):
        """
        Remove a specific proxy
        :param proxy_str: proxy string
        :return:
        """
        return await self.__conn.hdel(self.name, proxy_str)

    async def exists(self, proxy_str):
        """
        Check if a specific proxy exists
        :param proxy_str: proxy string
        :return: True if exists, False otherwise
        """
        try:
            return await self.__conn.hexists(self.name, proxy_str)
        except redis.ConnectionError as e:
            logger.error(f"Redis connection error: {e}")
            return False

    async def update(self, proxy_obj):
        """
        Update proxy attributes
        :param proxy_obj: Proxy object
        :return:
        """
        return await self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)

    async def getAll(self):
        """
        Return all proxies as a list of JSON strings
        :param https: whether to return only HTTPS proxies
        :return: list of proxies
        """
        items = await self.__conn.hvals(self.name)
        return [json.loads(item) for item in items]

    async def clear(self):
        """
        Clear all proxies
        :return:
        """
        return await self.__conn.delete(self.name)

    async def getCount(self):
        """
        Return the count of proxies
        :return: dict with total and https counts
        """
        proxies = await self.getAll()
        return {
            'total': len(proxies),
            'https': len(list(filter(lambda x: json.loads(x).get("https"), proxies)))
        }

    def changeTable(self, name):
        """
        Change the Redis hash name (table)
        :param name: new hash name
        :return:
        """
        self.name = name

    async def test(self):
        """
        Test the Redis connection
        :return: Exception if failed, False if successful
        """
        log = LogHandler('redis_client')
        try:
            return await self.getCount()
        except TimeoutError as e:
            log.error(f'Redis connection timeout: {e}', exc_info=True)
            return e
        except ConnectionError as e:
            log.error(f'Redis connection error: {e}', exc_info=True)
            return e
        except ResponseError as e:
            log.error(f'Redis response error: {e}', exc_info=True)
            return e
        except Exception as e:
            log.error(f'Unexpected error: {e}', exc_info=True)
            return e


if __name__ == '__main__':
    import asyncio

    kwargs = {'db': '0', 'host': '192.168.50.88', 'password': '', 'port': 6379, 'username': ''}
    res = asyncio.run(RedisClient(**kwargs).test())
    print(res)
