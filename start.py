# encoding=utf-8

import sys

from scrapy import cmdline

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
cmdline.execute("scrapy crawl api".split())
