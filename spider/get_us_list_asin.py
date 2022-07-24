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

url = 'https://www.amazon.com/s?i=merchant-items&me=A2GUMCXR7HBXM2&page=2&marketplaceID=ATVPDKIKX0DER&qid=1658676506&ref=sr_pg_2'

scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'linux',
                    'desktop': True,

                }
            )

res = scraper.get(url)
print(res.status_code)
with open("asin.html",'a+',encoding='utf-8') as f:
    f.write(res.text)