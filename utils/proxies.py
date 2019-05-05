import asyncio
import requests
from lxml.html import fromstring
from proxybroker import Broker


def get_proxies_list():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        # filter in HTTPS
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            # Grabbing IP and corresponding PORT
            proxy = ":".join([
                i.xpath('.//td[1]/text()')[0],
                i.xpath('.//td[2]/text()')[0]
            ])
            proxies.add(proxy)
    return proxies


async def __get_proxies(proxies):
    final_proxies = set()
    while True:
        proxy = await proxies.get()
        if proxy is None:
            break
        row = '%s:%d' % (proxy.host, proxy.port)
        final_proxies.add(row)
    return final_proxies


def get_proxies(proxy_type=['HTTPS']):
    proxies = asyncio.Queue()
    broker = Broker(proxies)
    tasks = asyncio.gather(
        broker.find(types=proxy_type, limit=20),
        __get_proxies(proxies))
    loop = asyncio.get_event_loop()
    proxy_list = loop.run_until_complete(tasks)[-1]
    return proxy_list


def __is_proxy_working(proxy):
    try:
        url = "https://httpbin.org/ip"
        requests.get(
            url, proxies={
                "http": proxy, "https": proxy},
            timeout=6)
        return True
    except Exception:
        return False


def get_working_proxy(proxy_pool):
    while True:
        proxy = next(proxy_pool)
        if __is_proxy_working(proxy):
            return proxy


if __name__ == "__main__":
    print("10 HTTPS proxy list")
    print(get_proxies())
