import cloudscraper
from datetime import datetime
from lxml import etree
import os,sys
import time
import django
pwd = os.path.dirname(os.path.realpath(__file__))
# 获取项目名的目录(因为我的当前文件是在项目名下的文件夹下的文件.所以是../)
sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AmazonProductsScout.settings")
django.setup()

from product.models import SellerBase,SellerDetail
from django.utils import timezone

url = 'https://www.amazon.com/s?i=merchant-items&me=AWZ6H68STFCI4&marketplaceID=ATVPDKIKX0DER&qid=1658906458&ref=sr_pg_1'
#url = 'http://httpbin.org/cookies'

scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'linux',
                    'desktop': True,
                }
            )
headers = {
    'Content-Type' : 'text/html;charset=UTF-8',
    'Cookie':'session-id=145-6781031-6397039; i18n-prefs=USD; ubid-main=135-5899715-9584050; lc-main=en_US; session-id-time=2082787201l; '
}
res = scraper.get(url,headers=headers)
print(res.status_code)
with open('asin.html','a+',encoding='utf-8') as f:
    f.write(res.text)