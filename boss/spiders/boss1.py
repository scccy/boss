# -*- coding: utf-8 -*-

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from boss.items import bossitem, FirstItemLoader




class Boss1Spider(CrawlSpider):
    name = 'boss'
    allowed_domains = ['www.zhipin.com']
    start_urls = ['https://www.zhipin.com']
    rules = (
        Rule(LinkExtractor(allow=('www.zhipin.com/job_detail/?query=数据标注&scity=100010000&industry=&position=',)),
             follow=True),
        Rule(LinkExtractor(allow=('www.zhipin.com/job_detail/\d+.html', )), callback='parse_item')

    )



    def parse_item(self, response):
        item_loader = FirstItemLoader(item=bossitem(), response=response)
        item_loader.add_xpath("title", "/html/body/div[1]/div[2]/div[1]/div/div/div[2]/div[2]/h1/text()")
        item_loader.add_xpath("city", "/html/body/div[1]/div[2]/div[1]/div/div/div[2]/p/text()")
        item_loader.add_value("url", response.url)
        item_loader.add_xpath("work_years", "/html/body/div[1]/div[2]/div[1]/div/div/div[2]/p/text()")
        item_loader.add_xpath("tags", "/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div[1]/div/text()")
        item_loader.add_value("id", response.url)
        job_item = item_loader.load_item()

        return job_item

