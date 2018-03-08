# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from __future__ import unicode_literals
from scrapy import signals
from selenium import webdriver
from scrapy.http import HtmlResponse
from scrapy import signals
from scrapy.signalmanager import SignalManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from fake_useragent import UserAgent
from scrapy.responsetypes import responsetypes
from scrapy.xlib.pydispatch import dispatcher
from selenium import webdriver
from six.moves import queue
from twisted.internet import defer, threads
from twisted.python.failure import Failure
from boss.tools.get_ip import Get_ip


class BossSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class BossDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)






class chromeDownloaderMiddleware(object):
    def __init__(self):
        # get_ip = Get_ip()
        # proxy = get_ip.random_ip()
        ua = UserAgent()
        headers = ua.random
        dcap = dict(DesiredCapabilities.CHROME)
        dcap["Chrome.page.settings.loadImages"] = True
        dcap["Chrome.page.settings.userAgent"] = headers
        # chromeOptions.add_argument('--proxy-server="{0}"'.format(proxy))
        self.Chromeoptions = webdriver.ChromeOptions()
        self.Chromeoptions.add_argument('--headless')
        self.sem = defer.DeferredSemaphore(10)
        self.queue = queue.LifoQueue(self.Chromeoptions)
        SignalManager(dispatcher.Any).connect(self._close, signal=signals.spider_closed)

    def _close(self):
        while not self.queue.empty():
            driver = self.queue.get_nowait()
            driver.close()

    def download_request(self, request, spider):
        """use semaphore to guard a phantomjs pool"""
        return self.sem.run(self._wait_request, request, spider)

    def _wait_request(self, request, spider):
        try:
            driver = self.queue.get_nowait()
        except queue.Empty:
            driver = webdriver.Chrome()

        driver.get(request.url)
        dfd = threads.deferToThread(lambda: driver.switch_to.window(driver.current_window_handle))
        dfd.addCallback(self._response, driver, spider)
        return dfd

    def _response(self, _, driver, spider):
        body = driver.execute_script("return document.documentElement.innerHTML")
        if body.startswith("<head></head>"):  # cannot access response header in Selenium
            body = driver.execute_script("return document.documentElement.textContent")
        url = driver.current_url
        respcls = responsetypes.from_args(url=url, body=body[:100].encode('utf8'))
        resp = respcls(url=url, body=body, encoding="utf-8")

        response_failed = getattr(spider, "response_failed", None)
        if response_failed and callable(response_failed) and response_failed(resp, driver):
            driver.close()
            return defer.fail(Failure())
        else:
            self.queue.put(driver)
            return defer.succeed(resp)