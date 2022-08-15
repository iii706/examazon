# -*- coding: utf-8 -*-
import cloudscraper
from datetime import datetime,timedelta
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
from django.core.paginator import Paginator
from django.utils import timezone
#print(datetime.now().strftime ('%Y-%m-%d %H:%M:%S'))


def get_page_content(seller_id):
    while True:
        try:
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'linux',
                    'desktop': True,

                }
            )

            # scraper = cloudscraper.create_scraper()
            res = scraper.get('https://www.amazon.com/sp?ie=UTF8&seller=%s&isAmazonFulfilled=1' % seller_id, timeout=15)
            print('https://www.amazon.com/sp?ie=UTF8&seller=%s&isAmazonFulfilled=1' % seller_id,res.status_code)
            if res.status_code == 200:
                return res
            else:
                time.sleep(5)
                continue
        except Exception as e:
            print(e)
            time.sleep(5)
            continue

while True:
    try:
        sellerbases = SellerBase.objects.filter(last_product_counts=0,display=True).order_by("mod_time").exclude(country='CN')[:1]
    except Exception as e:
        print('获取远程数据错误！！',e)
        time.sleep(5)
        continue
    if len(sellerbases) > 0:
        sellerbase = sellerbases[0]
        crawl_day = (timezone.now() - sellerbase.mod_time).days
        add_mod_day = (sellerbase.add_time - sellerbase.mod_time).days
        seller_id = sellerbase.seller_id
        print(seller_id)
        if seller_id == '':
            sellerbase.delete()
            continue
        res = get_page_content(seller_id)
        selector = etree.HTML(res.text)
        title = selector.xpath("//title/text()")
        sellerbase.brand_name = ''.join(selector.xpath('//*[@id="sellerName-rd"]/text()'))
        ratings_infos = selector.xpath('//table[@id="feedback-summary-table"]//tr[5]//td//text()')
        if len(ratings_infos) == 5:
            sellerbase.last_days_30_ratings = ratings_infos[1].replace(",", "")
            sellerbase.last_days_90_ratings = ratings_infos[2].replace(",", "")
            sellerbase.last_year_ratings = ratings_infos[3].replace(",", "")
            sellerbase.last_life_ratings = ratings_infos[4].replace(",", "")
        sellerbase.business_name = ''.join(
            selector.xpath('//div[@id="page-section-detail-seller-info"]/div/div/div/div[2]/span[2]/text()'))
        sellerbase.business_addr = "|".join(selector.xpath('//div[@class="a-row a-spacing-none indent-left"]//text()'))
        sellerbase.country = sellerbase.business_addr.split('|')[-1]
        # seller.add_time =
        print(sellerbase.brand_name, ratings_infos, sellerbase.business_name, sellerbase.business_addr)
        sellerbase.save()
    else:
        print('没有需要更新的卖家数据')
        time.sleep(60*3)

