# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Takenumber
from scrapy.loader import ItemLoader


def get_city(value):
    r = re.findall('城市：(\w*)', str(value))[0]
    return r


def replace_splash(value):
    addr_list = value.strip()
    return addr_list


def get_id(value):
    value = str(value)
    r = re.findall('(\d+)', value)
    return r


class Takethreed(object):
    def __call__(self, values):
        for i in range(len(values)):
            if i == 3:
                if values[i] is not None and values[i] != '':
                    return values[i]


class FirstItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class bossitem(scrapy.Field):
    title = scrapy.Field()
    url = scrapy.Field()
    city = scrapy.Field(input_processor=MapCompose(get_city))
    work_years = scrapy.Field(output_processor=Takethreed())
    tags = scrapy.Field(input_processor=MapCompose(replace_splash))
    id = scrapy.Field(input_processor=MapCompose(get_id))



    def get_insert_sql(self):
        insert_sql = """
            insert into boss_job(title, url, city, work_years, tags, id)
            VALUES (%s, %s, %s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE id=VALUES(id), title=VALUES(title), url=VALUES(url),
              city=VALUES(city), work_years=VALUES(work_years), 
              tags=VALUES(tags) 
        """
        params = (self["title"], self["url"], self["city"], self["work_years"], self["tags"], self["id"])
        return insert_sql, params