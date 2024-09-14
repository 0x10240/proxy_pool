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

FETCHER_COMMON_SOURCE = [
    {
        'url': 'http://api.89ip.cn/tqdl.html?api=1&num=8000&port=&address=&isp=',
        'type': 'http',
        'source': '89ip'
    },
    {
        'url': 'https://www.proxy-list.download/api/v1/get?type=http',
        'type': 'http',
        'source': 'proxy-list.download'
    },
    {
        'url': 'https://www.proxy-list.download/api/v1/get?type=socks4',
        'type': 'socks4',
        'source': 'proxy-list.download'
    },
    {
        'url': 'https://www.proxy-list.download/api/v1/get?type=socks5',
        'type': 'socks5',
        'source': 'proxy-list.download'
    },
    {
        'url': 'https://api.proxyscrape.com/?request=displayproxies&proxytype=http',
        'type': 'http',
        'source': 'proxyscrape'
    },
    {
        'url': 'https://api.proxyscrape.com/?request=displayproxies&proxytype=socks4',
        'type': 'socks4',
        'source': 'proxyscrape'
    },
    {
        'url': 'https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5',
        'type': 'socks5',
        'source': 'proxyscrape'
    },
    {
        'url': 'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt',
        'type': 'http',
        'source': 'zevtyardt/proxy-list'
    },
    {
        'url': 'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks4.txt',
        'type': 'socks4',
        'source': 'zevtyardt/proxy-list'
    },
    {
        'url': 'https://raw.githubusercontent.com/zevtyardt/proxy-list/main/socks5.txt',
        'type': 'socks5',
        'source': 'zevtyardt/proxy-list'
    },
    {
        'url': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
        'type': 'http',
        'source': 'TheSpeedX/PROXY-List'
    },
    {
        'url': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
        'type': 'socks4',
        'source': 'TheSpeedX/PROXY-List'
    },
    {
        'url': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
        'type': 'socks5',
        'source': 'TheSpeedX/PROXY-List'
    },
    {
        'url': 'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/http_proxies.txt',
        'type': 'http',
        'source': 'sunny9577/proxy-scraper'
    },
    {
        'url': 'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/socks4_proxies.txt',
        'type': 'socks4',
        'source': 'sunny9577/proxy-scraper'
    },
    {
        'url': 'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/generated/socks5_proxies.txt',
        'type': 'socks5',
        'source': 'sunny9577/proxy-scraper'
    },
    {
        'url': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
        'type': 'http',
        'source': 'monosans/proxy-list'
    },
    {
        'url': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
        'type': 'socks4',
        'source': 'monosans/proxy-list'
    },
    {
        'url': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
        'type': 'socks5',
        'source': 'monosans/proxy-list'
    },
    {
        'url': 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt',
        'type': 'http',
        'source': 'mmpx12/proxy-list'
    },
    {
        'url': 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt',
        'type': 'socks4',
        'source': 'mmpx12/proxy-list'
    },
    {
        'url': 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt',
        'type': 'socks5',
        'source': 'mmpx12/proxy-list'
    }
]

# ###### config the proxy fetch function ######
PROXY_FETCHER = [
    "common",
    "freeProxy11"
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

# ############# scheduler config #################

# Set the timezone for the scheduler forcely (optional)
# If it is running on a VM, and
#   "ValueError: Timezone offset does not match system offset"
#   was raised during scheduling.
# Please uncomment the following line and set a timezone for the scheduler.
# Otherwise it will detect the timezone from the system automatically.

TIMEZONE = "Asia/Shanghai"
