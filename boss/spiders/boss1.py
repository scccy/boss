# -*- coding: utf-8 -*-

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from boss.items import bossitem, FirstItemLoader
from selenium import webdriver
# from scrapy.xlib.pydispatch import dispatcher
# from scrapy import signals
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent
from boss.tools.get_ip import Get_ip


class Boss1Spider(CrawlSpider):
    name = 'boss'

    allowed_domains = ['www.zhipin.com']
    start_urls = ['https://www.zhipin.com']
    rules = (
        Rule(LinkExtractor(allow=('www.zhipin.com/job_detail/?query=数据标注&scity=100010000&industry=&position=',)), follow=True),
        Rule(LinkExtractor(allow=('www.zhipin.com/job_detail/\d+.html', )), callback='parse_item')

    )

    def __init__(self):
        # get_ip = Get_ip()
        # proxy = get_ip.random_ip()
        ua = UserAgent()
        headers = ua.random
        dcap = dict(DesiredCapabilities.CHROME)
        # dcap["Chrome.page.settings.loadImages"] = False
        dcap["Chrome.page.settings.userAgent"] = headers
        chromeOptions = webdriver.ChromeOptions()
        # chromeOptions.add_argument('--proxy-server="{0}"'.format(proxy))
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome()
        super(Boss1Spider, self).__init__()

        # dispatcher.connect(self.spider_close, signals.spider_closed)


    def spider_close(self):
        self.driver.quit()

    def parse_item(self, response):

        item_loader = FirstItemLoader(item=bossitem(), response=response)
        item_loader.add_xpath("title", "/html/body/div[1]/div[2]/div[1]/div/div/div[2]/div[2]/h1/text()")
        item_loader.add_xpath("city", "/html/body/div[1]/div[2]/div[1]/div/div/div[2]/p/text()")
        item_loader.add_value("url", response.url)
        item_loader.add_xpath("work_year", "/html/body/div[1]/div[2]/div[1]/div/div/div[2]/p/text()")
        item_loader.add_xpath("tag", "/html/body/div[1]/div[2]/div[3]/div/div[2]/div[3]/div[1]/div/text()")
        item_loader.add_value("id", response.url)
        job_item = item_loader.load_item()

        yield job_item

