# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyHandler.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/03:
                   2020/05/26: 区分http和https
-------------------------------------------------
"""
__author__ = 'JHao'

from helper.proxy import Proxy
from db.dbClient import DbClient
from handler.configHandler import ConfigHandler


class ProxyHandler(object):
    """ Proxy CRUD operator"""

    def __init__(self):
        self.conf = ConfigHandler()
        self.db = DbClient(self.conf.dbConn)
        self.db.changeTable(self.conf.tableName)

    async def get(self, https=False):
        """
        return a proxy
        Args:
            https: True/False
        Returns:
        """
        proxy = await self.db.get(https)
        return Proxy.createFromJson(proxy) if proxy else None

    async def pop(self, https):
        """
        return and delete a useful proxy
        :return:
        """
        proxy = await self.db.pop(https)
        if proxy:
            return Proxy.createFromJson(proxy)
        return None

    async def put(self, proxy):
        """
        put proxy into use proxy
        :return:
        """
        await self.db.put(proxy)

    async def delete(self, proxy):
        """
        delete useful proxy
        :param proxy:
        :return:
        """
        return await self.db.delete(proxy.proxy)

    async def getAll(self, type=None):
        """
        get all proxy from pool as Proxy list
        :return:
        """
        proxies = await self.db.getAll(type)
        return [Proxy.createFromJson(_) for _ in proxies]

    async def exists(self, proxy):
        """
        check proxy exists
        :param proxy:
        :return:
        """
        return await self.db.exists(proxy.proxy)

    async def getCount(self):
        """
        return raw_proxy and use_proxy count
        :return:
        """
        total_use_proxy = await self.db.getCount()
        return {'count': total_use_proxy}
