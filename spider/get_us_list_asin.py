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
#条件设定
REVIEW_COUNTS = 600
PAGE_COUNT = 15

from product.models import SellerBase,SellerDetail
from django.utils import timezone
from django.core.paginator import Paginator
from django.conf import settings


def get_page_content(url):
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
            res = scraper.get(url, timeout=10)
            print(res.status_code)
            if res.status_code == 200:
                return res
            else:
                time.sleep(5)
                continue
        except Exception as e:
            print(e)
            time.sleep(5)
            continue

def get_page_count(url):
    while True:
        try:
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'linux',
                    'desktop': True,

                }
            )
            res = scraper.get(url, timeout=10)
            print(res.status_code)
            if res.status_code == 200:
                selector = etree.HTML(res.text)
                # with open('asin.html','a+',encoding='utf-8') as f:
                #     f.write(res.text)
                # exit()
                results = selector.xpath('//div[@class="a-section a-spacing-small a-spacing-top-small"]/span/text()')
                print(results)
                if len(results) > 0:

                    products_count = results[0].replace('results', '').split('over')[-1].split("of")[-1].replace(',', '').strip()
                    sellerbase.last_product_counts = products_count
                    sellerbase.save()
                    #print(products_count)
                    page_count = int(int(products_count) / 16 + 1) if int(int(products_count) / 16 + 1) > 1 else int(
                        int(products_count) / 16 + 1) + 1
                    end_page = page_count if page_count <= PAGE_COUNT else PAGE_COUNT
                    return end_page
                else:
                    print('找不到产品，请检查ip是否是中国的ip')
                    return False
            else:
                time.sleep(5)
                continue
        except Exception as e:
            print(e)
            time.sleep(5)
            continue
def get_seller_page_count(page_size=100):
    seven_days = timezone.now() + timedelta(days=-7)
    sellerbases = SellerBase.objects.filter(last_product_counts=0,last_days_30_ratings__gt = 100).order_by("-id").exclude(country='CN')
    all_page = Paginator(sellerbases, page_size)
    return all_page.num_pages

def get_seller_page_data(page,page_size=100):
    seven_days = timezone.now() + timedelta(days=-7)
    sellerbases = SellerBase.objects.filter(last_product_counts=0,
                                            last_days_30_ratings__gt=100).order_by("-id").exclude(country='CN')
    all_page = Paginator(sellerbases,page_size)
    page_datas = all_page.page(page)
    return page_datas






sell_page_count = get_seller_page_count()
print("需要采集的卖家数总页数：",sell_page_count)

for seller_page in range(1,sell_page_count):
    page_datas = get_seller_page_data(seller_page)
    print(seller_page, sell_page_count)
    for page_data in page_datas:
        sellerbase = page_data
        url = 'https://www.amazon.com/s?i=merchant-items&me=%s&marketplaceID=ATVPDKIKX0DER&qid=1658906458&ref=sr_pg_1'%sellerbase.seller_id
        page_count = get_page_count(url)
        print("总页数：", page_count,url)
        for page in range(1,page_count):
            page_url = url = 'https://www.amazon.com/s?i=merchant-items&me=%s&page=%s&marketplaceID=ATVPDKIKX0DER&qid=1658906458&ref=sr_pg_%s'%(sellerbase.seller_id,str(page),str(page-1))
            res = get_page_content(page_url)
            selector = etree.HTML(res.text)
            products_eles = selector.xpath('//div[@class="s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16"]')
            asin_arr = []
            for products_ele in products_eles:
                asin = products_ele.xpath('./@data-asin')[0]
                reviews =products_ele.xpath('.//span[@class="a-size-base s-underline-text"]/text()')[0].replace(',','') if len(products_ele.xpath('.//span[@class="a-size-base s-underline-text"]/text()')) > 0 else 0
                #

                print(asin, reviews)
                if int(reviews) <= REVIEW_COUNTS:
                    asin_arr.append(asin)

            #删除过期的asin,已经采集过的
            # yesterday_score = int(time.mktime((datetime.now() + timedelta(days=-settings.ASIN_EXPIRE_DAY)).timetuple()))
            # settings.REDIS_CONN.zremrangebyscore(settings.PRODUCT_FILTER, 0, yesterday_score)
            print(page,'待采集的：',asin_arr)
            if len(asin_arr) > 0:
                # 加入抓取卖家id的asin队列，先过滤再加入
                pipe = settings.REDIS_CONN.pipeline()
                for asin in asin_arr:
                    pipe.zrank(settings.PRODUCT_FILTER, asin)
                ex_rets = pipe.execute()
                noex_asins = []
                for item in zip(ex_rets, asin_arr):
                    if item[0] == None:
                        noex_asins.append(item[1])
                # print("noex_asins",noex_asins)
                pipe = settings.REDIS_CONN.pipeline()
                for asin in noex_asins:
                    today_score = int(time.mktime(datetime.now().timetuple()))
                    pipe.zadd(settings.PRODUCT_WAIT, {asin: today_score}, nx=True, ch=True)  # 加进去待采集队列，score为当前时间戳
                pipe.execute()

# with open('asin.html','a+',encoding='utf-8') as f:
#     f.write(res.text)