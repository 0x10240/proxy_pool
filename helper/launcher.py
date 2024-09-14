# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     launcher
   Description :   Launcher
   Author :        JHao
   Date：          2021/3/26
-------------------------------------------------
   Change Activity:
                   2021/3/26: Launcher
                   2023/09/14: Adapted to use asynchronous scheduler
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
import asyncio
from db.dbClient import DbClient
from handler.logHandler import LogHandler
from handler.configHandler import ConfigHandler

log = LogHandler('launcher')


def startServer():
    __beforeStart()
    from api.proxyApi import runFastAPI
    runFastAPI()


def startScheduler():
    __beforeStart()
    from helper.scheduler import main as scheduler_main
    asyncio.run(scheduler_main())


def __beforeStart():
    __showVersion()
    __showConfigure()
    # If __checkDBConfig is asynchronous, adjust accordingly
    if asyncio.run(__checkDBConfig()):
        log.info('exit!')
        sys.exit()


def __showVersion():
    from setting import VERSION
    log.info("ProxyPool Version: %s" % VERSION)


def __showConfigure():
    conf = ConfigHandler()
    log.info("ProxyPool configure HOST: %s" % conf.serverHost)
    log.info("ProxyPool configure PORT: %s" % conf.serverPort)
    log.info("ProxyPool configure PROXY_FETCHER: %s" % conf.fetchers)


async def __checkDBConfig():
    conf = ConfigHandler()
    db = DbClient(conf.dbConn)
    log.info("============ DATABASE CONFIGURE ================")
    log.info("DB_TYPE: %s" % db.db_type)
    log.info("DB_HOST: %s" % db.db_host)
    log.info("DB_PORT: %s" % db.db_port)
    log.info("DB_NAME: %s" % db.db_name)
    log.info("DB_USER: %s" % db.db_user)
    log.info("=================================================")
    return await db.test()
