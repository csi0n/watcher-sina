# encoding=utf-8
import json
import base64
import requests

accounts = [
    {'username': 'chen655@163.com', 'password': '16fe3aa7de0edd58'}
    # {'username': 'shudieful3618@163.com', 'password': 'a123456'}
]


# 获取cookie
def getCookies(accounts):
    cookies = []
    loginUrl = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
    for account in accounts:
        username = base64.b64encode(account['username'].encode('utf-8')).decode('utf-8')
        password = account['password']
        postData = {
            "entry": "sso",
            "gateway": "1",
            "from": "null",
            "savestate": "30",
            "useticket": "0",
            "pagerefer": "",
            "vsnf": "1",
            "su": username,
            "service": "sso",
            "sp": password,
            "sr": "1440*900",
            "encoding": "UTF-8",
            "cdult": "3",
            "domain": "sina.com.cn",
            "prelt": "0",
            "returntype": "TEXT",
        }
        session = requests.Session()
        r = session.post(loginUrl, data=postData)
        jsonStr = r.content.decode('gbk')
        info = json.loads(jsonStr)
        if info["retcode"] == "0":
            print "get cookie success, current account is %s" % account
            cookie = session.cookies.get_dict()
            cookies.append(cookie)
        else:
            print "get cookie failed,reason is %s" % info['reason']
    return cookies


cookies = getCookies(accounts)
print "get cookies finish,num is %d" % len(cookies)
