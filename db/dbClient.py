# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     DbClient.py
   Description :   Database Factory Class
   Author :        JHao
   Date：          2016/12/2
-------------------------------------------------
   Change Activity:
                   2016/12/02:   Database Factory Class
                   2020/07/03:   Removed raw_proxy storage
                   2023/09/14:   Adapted to use asynchronous database clients
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import sys
import asyncio

from helper.proxy import Proxy
from util.six import urlparse, withMetaclass
from util.singleton import Singleton

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class DbClient(withMetaclass(Singleton)):
    """
    DbClient is a database factory class providing methods:
    get/put/update/pop/delete/exists/getAll/clear/getCount/changeTable

    Abstract method definitions:
        get(): Return a proxy randomly;
        put(proxy): Store a proxy;
        pop(): Return and delete a proxy sequentially;
        update(proxy): Update specified proxy information;
        delete(proxy): Delete specified proxy;
        exists(proxy): Check if specified proxy exists;
        getAll(): Return all proxies;
        clear(): Clear all proxy information;
        getCount(): Return proxy statistics;
        changeTable(name): Switch the operation object

    All methods need to be implemented by the corresponding class:
        ssdb: ssdbClient.py
        redis: redisClient.py
        mongodb: mongodbClient.py
    """

    def __init__(self, db_conn):
        """
        Initialize the database client
        """
        self.parseDbConn(db_conn)
        self.__initDbClient()

    @classmethod
    def parseDbConn(cls, db_conn):
        db_conf = urlparse(db_conn)
        cls.db_type = db_conf.scheme.upper().strip()
        cls.db_host = db_conf.hostname
        cls.db_port = db_conf.port
        cls.db_user = db_conf.username
        cls.db_pwd = db_conf.password
        cls.db_name = db_conf.path[1:]
        return cls

    def __initDbClient(self):
        """
        Initialize the database client
        """
        __type = None
        if "SSDB" == self.db_type:
            __type = "ssdbClient"
        elif "REDIS" == self.db_type:
            __type = "redisClient"
        else:
            pass
        assert __type, 'type error, Not support DB type: {}'.format(self.db_type)
        module = __import__(__type)
        client_class = getattr(module, "%sClient" % self.db_type.title())
        self.client = client_class(host=self.db_host,
                                   port=self.db_port,
                                   username=self.db_user,
                                   password=self.db_pwd,
                                   db=self.db_name)

    async def get(self, https, **kwargs):
        return await self.client.get(https, **kwargs)

    async def put(self, key, **kwargs):
        return await self.client.put(key, **kwargs)

    async def update(self, key, value, **kwargs):
        return await self.client.update(key, value, **kwargs)

    async def delete(self, key, **kwargs):
        return await self.client.delete(key, **kwargs)

    async def exists(self, key, **kwargs):
        return await self.client.exists(key, **kwargs)

    async def pop(self, https, **kwargs):
        return await self.client.pop(https, **kwargs)

    async def getAll(self, type=None):
        return await self.client.getAll(type)

    async def clear(self):
        return await self.client.clear()

    def changeTable(self, name):
        self.client.changeTable(name)

    async def getCount(self):
        return await self.client.getCount()

    async def test(self):
        return await self.client.test()

if __name__ == '__main__':
    p = Proxy("socks5://127.0.0.1:1080")
    print(p.to_json)