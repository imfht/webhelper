import json
import os
import random
import time
import urllib.robotparser
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup
from loguru import logger

VIA_PROXY = os.getenv('VIA_PROXY', '')
WS_TOKEN = os.getenv('WS_TOKEN', '')
proxy_list = []


class RequestNotSucceedException(Exception):
    pass


class RobotNotAllowedException(Exception):
    """不被robots.txt容许"""
    pass


class HtmlResponse():
    def __init__(self, text):
        self.text = text

    def to_soup(self):
        return BeautifulSoup(self.text, 'html.parser')

    def to_json(self):
        return json.loads(self.text)

    def to_html(self):
        return self.text

    def to_rss(self):
        item = feedparser.parse(self.text)
        return [i for i in item.entries]


def can_fetch(url):
    rp = urllib.robotparser.RobotFileParser()
    parsed_url = urlparse(url)
    robots_file = get_html(f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt", obey_robot=False)
    rp.parse(robots_file.text.split('\n'))
    return rp.can_fetch('*', url)


def get_a_proxy():
    proxy_url = random.choice(proxy_list)
    logger.trace("使用代理 %s" % proxy_url)
    return {'http': proxy_url, 'https': proxy_url}


def get_html(url, max_retries=3, timeout=10, obey_robot=True):
    """输入一个url, 返回html"""
    proxy = None
    if obey_robot:
        try:
            if not can_fetch(url) or os.getenv('VIA_PROXY'):
                proxy = get_a_proxy()
                logger.info("robots协议禁止抓取，使用匿名代理: %s" % proxy['http'])
                # raise RobotNotAllowedException()
        except Exception as e:
            raise RequestNotSucceedException()
    userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36'
    for i in range(max_retries):
        try:
            resp = requests.get(url, timeout=timeout, headers={"User-Agent": userAgent}, proxies=proxy)
            trace_msg = f"请求成功: {url}, 使用代理 {proxy}" if proxy else f"请求成功: {url}"
            logger.trace(trace_msg)
            if resp.status_code != 200:
                logger.warning(f"{url} status code {resp.status_code}")
            return HtmlResponse(resp.text)
        except Exception as e:
            logger.warning(e)
        finally:
            time.sleep(1)
    logger.exception(RequestNotSucceedException())


def set_global_random_proxy(ws_token):
    os.environ['VIA_PROXY'] = '1'
    global proxy_list
    response = requests.get("https://proxy.webshare.io/api/proxy/list/?page=1&countries=US-FR",
                            headers={"Authorization": ws_token}, timeout=10)
    proxy_list = [
        f'http://{proxy["username"]}:{proxy["password"]}@{proxy["proxy_address"]}:{proxy["ports"]["http"]}'
        for proxy in response.json()['result']]


if __name__ == '__main__':
    # assert can_fetch('https://about.gitlab.com/solutions/open-source/') is True
    # assert can_fetch('https://about.gitlab.com/handbook/ceo/shadow/setalarm.sh') is False
    # print(get_html('https://about.gitlab.com/handbook/ceo/shadow/setalarm.sh').text)
    print(get_a_proxy())
