# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     setting.py
   Description :   配置文件
   Author :        JHao
   date：          2019/2/15
-------------------------------------------------
   Change Activity:
                   2019/2/15:
-------------------------------------------------
"""

import os

current_dir = os.path.abspath(os.path.dirname(__file__))
datadir = os.path.realpath(os.path.join(current_dir, 'data'))

BANNER = r"""
****************************************************************
*** ______  ********************* ______ *********** _  ********
*** | ___ \_ ******************** | ___ \ ********* | | ********
*** | |_/ / \__ __   __  _ __   _ | |_/ /___ * ___  | | ********
*** |  __/|  _// _ \ \ \/ /| | | ||  __// _ \ / _ \ | | ********
*** | |   | | | (_) | >  < \ |_| || |  | (_) | (_) || |___  ****
*** \_|   |_|  \___/ /_/\_\ \__  |\_|   \___/ \___/ \_____/ ****
****                       __ / /                          *****
************************* /___ / *******************************
*************************       ********************************
****************************************************************
"""

VERSION = "2.4.0"

# ############### server config ###############
HOST = "0.0.0.0"

PORT = 5010

# ############### database config ###################
# db connection uri
# example:
#      Redis: redis://:password@ip:port/db
#      Ssdb:  ssdb://:password@ip:port
DB_CONN = 'redis://:@192.168.50.88:6379/0'

# proxy table name
TABLE_NAME = 'use_proxy'

with open(os.path.join(datadir, 'socks5.txt'), 'r') as f:
    socks5_urls = f.readlines()

FETCHER_COMMON_SOURCE = []

socks5_urls = [x.strip() for x in socks5_urls if x.strip()]
for url in socks5_urls:
    if url.startswith('https://raw.githubusercontent.com/'):
        s = url.replace('https://raw.githubusercontent.com/', '')
        source = '/'.join(s.split('/')[:2])
    else:
        source = url.split('/')[2]
    FETCHER_COMMON_SOURCE.append({
        'url': url,
        'type': 'socks5',
        'source': source,
    })

# ###### config the proxy fetch function ######
PROXY_FETCHER = [
    "common",
    "geonode",
    "advanced_name",
]

# ############# proxy validator #################
# 代理验证目标网站
HTTP_URL = "http://httpbin.org"
HTTPS_URL = "https://www.qq.com"
SOCKS_utl = "https://www.qq.com"

# 代理验证时超时时间
VERIFY_TIMEOUT = 3

# 近PROXY_CHECK_COUNT次校验中允许的最大失败次数,超过则剔除代理
MAX_FAIL_COUNT = 0

# 近PROXY_CHECK_COUNT次校验中允许的最大失败率,超过则剔除代理
# MAX_FAIL_RATE = 0.1

# proxyCheck时代理数量少于POOL_SIZE_MIN触发抓取
POOL_SIZE_MIN = 20

# ############# proxy attributes #################
# 是否启用代理地域属性
PROXY_REGION = True

TIMEZONE = "Asia/Shanghai"

if __name__ == '__main__':
    for item in FETCHER_COMMON_SOURCE:
        print(item)
