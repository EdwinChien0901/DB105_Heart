# -*- coding: utf-8 -*-
import scrapy
import time
import random
from spider_xuite.items import SpiderXuiteItem


class FirstSpiderSpider(scrapy.Spider):
    name = 'first_spider'
    allowed_domains = ['yo.xuite.net']
    area_search_list = ['台北', '新北', '基隆', '桃園','宜蘭']
    url_part1 = 'https://yo.xuite.net/info/search.php?keyword='
    url_part2 = '&k=spot&p='

    start_urls = []

    for area in area_search_list:

        for page in range(1, 38):

            start_urls.append(url_part1 + area + url_part2 + str(page))

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }

    def parse(self, response):

        res = response.xpath('//*[@id="componet-element-list"]/li/a[2]//@href').extract()

        for u in res:

            # sleeptime = random.randint(0, 3)
            #
            # time.sleep(sleeptime)

            urls = 'https://yo.xuite.net' + str(u)
            # print(urls)
            # print("爬取結束")
            yield scrapy.Request(urls, self.parse_item, headers=self.headers)

    def parse_item(self, response):

        item = SpiderXuiteItem()

        item['places'] = response.xpath('//*[@id="element-info-title"]/text()').extract()

        raw_content= response.xpath('//*[@id="element-describe-content"]//text()').extract()

        for bb, reqq in enumerate(raw_content):

            raw_content[bb] = reqq.strip()

        raw_content = list(filter(None, raw_content))#filter進行過濾

        item['contents'] = "".join(raw_content)

        return item
