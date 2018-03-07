# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from twisted.enterprise import adbapi
import pymysql
import pymysql.cursors





class mysql_insert_match_point(object):

    def __init__(self, dbpool_match):
        self.dbpool_match = dbpool_match

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DB"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )
        dbpool_match = adbapi.ConnectionPool("pymysql", **dbparms)

        return cls(dbpool_match)

    def handle_error(self, failure, itme, spider):
        print(failure)

    def insert_do(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)

    def process_item(self, item, spider):
        query = self.dbpool_match.runInteraction(self.insert_do, item)
        query.addErrback(self.handle_error, item, spider)
