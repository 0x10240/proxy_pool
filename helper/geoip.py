import os

import aiohttp
import asyncio
import geoip2.database
from loguru import logger
from geoip2.errors import AddressNotFoundError
from aiohttp_socks import ProxyConnector

current_dir = os.path.abspath(os.path.dirname(__file__))

database_dir = os.path.realpath(os.path.join(current_dir, '../data/'))
city_data = geoip2.database.Reader(os.path.join(database_dir, "GeoLite2-City.mmdb"))
ans_data = geoip2.database.Reader(os.path.join(database_dir, "GeoLite2-ASN.mmdb"))


async def parse_location(proxy_str):
    logger.info("Starting parse location.")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }
    url = "https://api.ip.sb/geoip"

    proxy, connector = None, None
    if proxy_str.startswith("http"):
        proxy = proxy_str
    elif proxy_str.startswith("socks"):
        connector = ProxyConnector.from_url(proxy_str)

    timeout = aiohttp.ClientTimeout(total=5)

    try:
        async with aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=headers,
        ) as session, session.get(url, proxy=proxy, ssl=False) as response:
            tmp = await response.json()
            logger.info(
                f'IP: {tmp["ip"]}, '
                f'Server Country Code : {tmp["country_code"]}, '
                f'Continent Code : {tmp["continent_code"]}, '
                f'ISP : {tmp["organization"]}'
            )
            return True, tmp["country_code"], tmp["continent_code"], tmp["organization"]
    except asyncio.TimeoutError:
        logger.error("Parse location timeout.")
    except Exception as e:
        logger.error(f"Parse location failed: {repr(e)}")
    return False, "DEFAULT", "DEFAULT", "DEFAULT"


def query_geo_local(ip):
    country, city, organization = "N/A", "N/A", "N/A"
    try:
        country_info = city_data.city(ip).country
        country = country_info.names.get("en", "N/A")
        city = city_data.city(ip).city.names.get("en", "N/A")
        organization = (
            ans_data.asn(ip)
            .autonomous_system_organization.replace(" Communications Co.,Ltd", "")
            .replace(" communications corporation", "")
        )
    except ValueError as e:
        logger.error(e)
    except AddressNotFoundError as e:
        logger.error(e)
    return {"country": country, "city": city, "organization": organization}


def get_geo_info(ip):
    info = query_geo_local(ip)
    ret = f"{info.get('country', 'N/A')}, {info.get('city', 'N/A')}, {info.get('organization', 'N/A')}"
    logger.info(f'ip: {ip}, geo info: {ret}')
    return ret


if __name__ == '__main__':
    import requests

    for _ in range(100):
        proxy = requests.get('http://192.168.50.88:5010/get?type=http').json().get('proxy')
        logger.info(f"proxy: {proxy}")
        ret = asyncio.run(parse_location(proxy))
        print(ret)
