import aiohttp
import asyncio
import random
from handler.logHandler import LogHandler


class WebRequest:
    name = "web_request"

    def __init__(self, *args, **kwargs):
        self.log = LogHandler(self.name, file=False)
        self.response = None

    @property
    def user_agent(self):
        """
        Return a random User-Agent
        """
        ua_list = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
            'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        ]
        return random.choice(ua_list)

    @property
    def headers(self):
        """
        Basic headers
        """
        return {
            'User-Agent': self.user_agent,
            'Accept': '*/*',
            'Connection': 'keep-alive',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }

    async def get(self, url, headers=None, retry_time=3, retry_interval=5, timeout=5, *args, **kwargs):
        merged_headers = self.headers.copy()
        if headers and isinstance(headers, dict):
            merged_headers.update(headers)

        while retry_time > 0:
            try:
                async with aiohttp.ClientSession(headers=merged_headers) as session:
                    async with session.get(url, timeout=timeout, *args, **kwargs) as response:
                        status = response.status
                        content = await response.text()
                        return status, content
            except Exception as e:
                self.log.error(f"Request to {url} failed: {e}")
                retry_time -= 1
                if retry_time <= 0:
                    return None, None

                self.log.info(f"Retrying in {retry_interval} seconds...")
                await asyncio.sleep(retry_interval)

        return None, None
