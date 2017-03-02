# encoding=utf-8
import smtplib
import sys
import textwrap
from email.header import Header
from email.mime.text import MIMEText

from scrapy import cmdline

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
cmdline.execute("scrapy crawl api".split())