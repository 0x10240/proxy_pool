# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyApi.py
   Description :   API using FastAPI with async support
   Author :        JHao
   Date：          2023/09/14
-------------------------------------------------
   Change Activity:
                   2023/09/14: Rewritten using FastAPI with async support
-------------------------------------------------
"""
__author__ = 'JHao'

import json
import platform
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from helper.proxy import Proxy
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler

app = FastAPI()
conf = ConfigHandler()
proxy_handler = ProxyHandler()

api_list = [
    {"url": "/get", "params": "type: 'https' or ''", "desc": "get a proxy"},
    {"url": "/pop", "params": "type: 'https' or ''", "desc": "get and delete a proxy"},
    {"url": "/delete", "params": "proxy: 'e.g. 127.0.0.1:8080'", "desc": "delete an unable proxy"},
    {"url": "/all", "params": "type: 'https' or ''", "desc": "get all proxies from proxy pool"},
    {"url": "/count", "params": "", "desc": "return proxy count"}
]


class ProxyModel(BaseModel):
    proxy: str
    https: bool
    fail_count: int
    region: str
    anonymous: str
    source: str
    check_count: int
    last_status: str
    last_time: str


@app.get("/", response_class=JSONResponse)
async def index():
    return {"url": api_list}


@app.get("/get/")
async def get_proxy(type: Optional[str] = Query(default="", description="Type of proxy: 'https' or ''")):
    type = type.lower()
    proxy = await proxy_handler.get(type)
    return proxy if proxy else {"code": 0, "src": "no proxy"}


@app.get("/pop/")
async def pop_proxy(type: Optional[str] = Query(default="", description="Type of proxy: 'https' or ''")):
    https = type.lower() == 'https'
    proxy = await proxy_handler.pop(https)
    if proxy:
        return proxy.to_dict
    else:
        return {"code": 0, "src": "no proxy"}


@app.get("/refresh/")
async def refresh():
    # TODO: The refresh operation is handled by a scheduled task. Direct API calls may have poor performance.
    return {"message": "success"}


@app.get("/all/", response_model=List[Dict[str, Any]])
async def get_all(
        type: Optional[str] = Query(default="", description="Type of proxy: 'https' or ''"),
        source: Optional[str] = Query(default="", description="source of proxy"),
        valid: Optional[bool] = Query(default=False, description="is proxy valid"),
        count: Optional[int] = Query(default=0, description="count of proxy"),
):
    proxies = await proxy_handler.getAll()
    # proxies.sort(key=lambda x: x.get('last_time', ''), reverse=True)

    if type:
        proxies = [proxy for proxy in proxies if source in proxy.get("type") == type]

    if source:
        proxies = [proxy for proxy in proxies if source in proxy.get("source")]

    if valid:
        proxies = [proxy for proxy in proxies if proxy.get("last_status") and proxy.get("outbound_ip")]

    if count > 0:
        proxies = proxies[:count]

    return proxies


@app.get("/delete/")
async def delete_proxy(proxy: str):
    status = await proxy_handler.delete(Proxy(proxy))
    return {"code": 0, "src": status}


@app.get("/count/")
async def get_count():
    return await proxy_handler.getCount()


def runFastAPI():
    import uvicorn
    if platform.system() == "Windows":
        uvicorn.run(app, host=conf.serverHost, port=conf.serverPort)
    else:
        uvicorn.run("api.proxyApi:app", host=conf.serverHost, port=conf.serverPort, workers=4)


if __name__ == '__main__':
    runFastAPI()
