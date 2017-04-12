# encoding=utf-8
import re
import smtplib
import time
from email.header import Header
from email.mime.text import MIMEText

import MySQLdb
import requests
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.spider import CrawlSpider

from api import config
from api.items import TweetsItem


class Spider(CrawlSpider):
    name = "api"
    host = "http://weibo.cn"

    def start_requests(self):
        scrawl_ID = self.GetSinaWatcherUsers()
        while scrawl_ID.__len__():
            ID = scrawl_ID.pop()
            tempId = ID
            ID = str(ID['uid'])
            self.ID = ID
            self.EMAIL = tempId['email']
            url_tweets = "http://weibo.cn/%s/profile?filter=1&page=1" % ID
            yield Request(url=url_tweets, meta={"ID": ID}, callback=self.parse2)  # 去爬微博

    def parse2(self, response):
        selector = Selector(response)
        tweets = selector.xpath('body/div[@class="c" and @id]')
        flag_save_update = True
        for tweet in tweets:
            tweetsItems = TweetsItem()
            id = tweet.xpath('@id').extract_first()  # 微博ID
            content = tweet.xpath('div/span[@class="ctt"]/text()').extract_first()  # 微博内容
            cooridinates = tweet.xpath('div/a/@href').extract_first()  # 定位坐标
            like = re.findall(u'\u8d5e\[(\d+)\]', tweet.extract())  # 点赞数
            transfer = re.findall(u'\u8f6c\u53d1\[(\d+)\]', tweet.extract())  # 转载数
            comment = re.findall(u'\u8bc4\u8bba\[(\d+)\]', tweet.extract())  # 评论数
            others = tweet.xpath('div/span[@class="ct"]/text()').extract_first()  # 求时间和使用工具（手机或平台）

            tweetsItems["ID"] = response.meta["ID"]
            tweetsItems["_id"] = response.meta["ID"] + "-" + id
            if content:
                tweetsItems["Content"] = content.strip(u"[\u4f4d\u7f6e]")  # 去掉最后的"[位置]"
            if cooridinates:
                cooridinates = re.findall('center=([\d|.|,]+)', cooridinates)
                if cooridinates:
                    tweetsItems["Co_oridinates"] = cooridinates[0]
            if like:
                tweetsItems["Like"] = int(like[0])
            if transfer:
                tweetsItems["Transfer"] = int(transfer[0])
            if comment:
                tweetsItems["Comment"] = int(comment[0])
            if others:
                others = others.split(u"\u6765\u81ea")
                tweetsItems["PubTime"] = others[0]
                if len(others) == 2:
                    tweetsItems["Tools"] = others[1]
            weibo = self.GetSinaLastWeiBoByUid(tweetsItems['ID'])
            if weibo:
                if tweetsItems['Content'].encode('UTF-8', 'ignore') == weibo['last_content']:
                    print "微博内容相同跳出循环！"
                    break
                else:
                    if flag_save_update:
                        print "更新第一条微博"
                        emotion = self.GetEmotion(tweetsItems['Content'])
                        tweetsItems['emotion'] = emotion['emotion']
                        self.updateWeibo(tweetsItems)
                        flag_save_update = False
                    self.sendEmail(tweetsItems)
            else:
                emotion = self.GetEmotion(tweetsItems['Content'])
                tweetsItems['emotion'] = emotion['emotion']
                yield tweetsItems
                print "新增用户%d" % (int(tweetsItems['ID']))
                self.sendEmail(tweetsItems)
                break

    def GetDb(self):
        db = MySQLdb.connect(host=config.DB_HOST, user=config.DB_USER, passwd=config.DB_PASSWORD, db=config.DB_NAME,
                             port=config.DB_PORT, charset="utf8")
        self.db=db
        return db.cursor()

    def GetSinaWatcherUsers(self):
        cursor = self.GetDb()
        sql = "SELECT * FROM watcher_users"
        cursor.execute(sql)
        results = cursor.fetchall()
        uids = []
        for row in results:
            uids.append({"uid": int(row[1]), "email": row[2]})
        return uids

    def GetSinaLastWeiBoByUid(self, uid):
        cursor = self.GetDb()
        sql = "select * from sina where uid='%s'" % (str(uid))
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            return {
                "uid": result[0],
                "last_content": result[1],
                "tools": result[2],
                "likes": result[3],
                "comments": result[4],
                "transfer": result[5],
                "public_time": result[6]
            }
        else:
            return None

    def updateWeibo(self, tweetsItems):
        if isinstance(tweetsItems, TweetsItem):
            try:
                cursor = self.GetDb()
                sql = "UPDATE sina SET last_content='%s',tools='%s',likes='%d',comments='%d',transfer='%d',public_time='%s',emotion='%d',update_time='%d' WHERE uid='%s'" % (
                    tweetsItems['Content'], tweetsItems['Tools'], tweetsItems['Like'],
                    tweetsItems['Comment'], tweetsItems['Transfer'], tweetsItems['PubTime'], tweetsItems['emotion'],
                    time.time(), tweetsItems['ID'])
                print sql
                cursor.execute(sql)
        
            except MySQLdb.Error, e:
                print e
                pass

    def GetEmotion(self, content):
        url = "https://api.prprpr.me/emotion/?text=%s" % (content)
        r = requests.get(url)
        return r.json()

    def sendEmail(self, tweetsItem):
        if isinstance(tweetsItem, TweetsItem):
            sender = 'service@csi0n.com'
            receivers = [self.EMAIL]
            message = MIMEText("<!DOCTYPE html><html><head>" \
                               "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\" />" \
                               "<title>分析报告</title></head>" \
                               "<body>内容:%s<br/>平台:%s<br/>发布时间:%s<br/>心情指数:%d<br/></body>\
                               </html>" % (
                                   tweetsItem['Content'], tweetsItem['Tools'], tweetsItem['PubTime'],
                                   tweetsItem['emotion']), "html", "utf-8")
            message['From'] = Header('csi0n', 'utf-8')
            message['To'] = Header("%s" % (self.EMAIL), 'utf-8')
            subject = "用户ID为:%s 发表了一篇新的微博,系统分析报告如下" % (str(tweetsItem['ID']))
            message['Subject'] = Header(subject, 'utf-8')
            try:
                smtpObj = smtplib.SMTP('')
                smtpObj.login(sender, "")
                smtpObj.sendmail(sender, receivers, message.as_string())
                print "邮件发送成功"
            except smtplib.SMTPException, e:
                print "发送邮件失败", e
