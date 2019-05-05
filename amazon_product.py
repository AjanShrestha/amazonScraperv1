import csv
import json
import os
from itertools import cycle
from random import randint
from time import sleep

import requests
from lxml import html
from fake_useragent import UserAgent

from utils.proxies import get_proxies, get_working_proxy


def parse(url, proxy):
    ua = UserAgent(cache=False)
    headers = {
        'User-Agent': ua.random
    }
    try:
        # Retrying for failed requests
        for _ in range(5):
            # Generating random delays
            sleep(randint(1, 3))
            # Adding verify=False to avold ssl related issues
            response = requests.get(
                url, headers=headers, proxies={"https": proxy})

            if response.status_code == 200:
                doc = html.fromstring(response.content)
                XPATH_NAME = '//span[@id = "productTitle"]//text()'
                XPATH_SALE_PRICE = '//span[contains(@id, "priceblock_ourprice") or contains(@id, "saleprice")]/text()'
                XPATH_CATEGORY = '//a[@class="a-link-normal a-color-tertiary"]//text()'
                XPATH_AVAILABILITY = '//div[@id="availability"]/span//text()'

                RAW_NAME = doc.xpath(XPATH_NAME)
                RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
                RAW_CATEGORY = doc.xpath(XPATH_CATEGORY)
                RAW_AVAILABILITY = doc.xpath(XPATH_AVAILABILITY)

                NAME = ' '.join(''.join(RAW_NAME).split()
                                ) if RAW_NAME else None
                SALE_PRICE = ' > '.join(
                    ''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
                CATEGORY = ' > '.join(
                    [i.strip() for i in RAW_CATEGORY]) if RAW_CATEGORY else None
                AVAILABILITY = ''.join(
                    RAW_AVAILABILITY).strip() if RAW_AVAILABILITY else None

                # retrying in case of captcha
                if not NAME:
                    raise ValueError('captcha')

                data = {
                    'NAME': NAME,
                    'SALE_PRICE': SALE_PRICE,
                    'CATEGORY': CATEGORY,
                    'AVAILABILITY': AVAILABILITY,
                    'URL': url
                }
                return data
            elif response.status_code == 404:
                break
    except Exception as e:
        print(e)


def ReadAsin(proxy_pool):
    AsinList = csv.DictReader(
        open(os.path.join(os.path.dirname(__file__), "Asinfeed.csv")))
    extracted_data = []
    for AsinValue in AsinList:
        proxy = get_working_proxy(proxy_pool)
        url = "http://www.amazon.com/dp/" + AsinValue["ASIN"]
        print("Processing: " + url)
        # Calling the parser
        parsed_data = parse(url, proxy)
        if parsed_data:
            extracted_data.append(parsed_data)
    return extracted_data


def write_extracted(extracted_data):
    # Writing scraped data to csv file
    with open('scraped_data.csv', 'w') as csvfile:
        fieldnames = [
            'NAME', 'SALE_PRICE', 'CATEGORY',
            'AVAILABILITY', 'URL']
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in extracted_data:
            writer.writerow(data)


if __name__ == "__main__":
    proxies = get_proxies()
    proxy_pool = cycle(proxies)
    write_extracted(ReadAsin(proxy_pool))
