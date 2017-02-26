# encoding=utf-8
import time

import MySQLdb

from items import TweetsItem


class MysqlDbPipleline(object):
    def __init__(self):
        self.db = MySQLdb.connect(host='127.0.0.1', user="root", passwd="123456", db="sina", port=3306, charset="utf8")
        self.cursor = self.db.cursor()

    def closeDb(self):
        self.db.close()

    def process_item(self, item, spider):
        if isinstance(item, TweetsItem):
            sql = "insert into sina (uid,last_content,tools,likes,comments,transfer,public_time,emotion,update_time) VALUES (" \
                  "'%s','%s','%s','%d','%d','%d','%s',%d,%d)" % (
                      item['ID'], item['Content'], item['Tools'], item['Like'], item['Comment'], item['Transfer'],
                      item['PubTime'], int(item['emotion']), time.time())
            try:
                self.cursor.execute(sql)
                self.db.commit()
            except MySQLdb.Error, e:
                print e
                self.db.rollback()
                pass
