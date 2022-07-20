import cloudscraper
from datetime import datetime
import time,random
from lxml import etree
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import sys
import os

from django.utils.safestring import mark_safe

# 获取当前文件的目录
pwd = os.path.dirname(os.path.realpath(__file__))
# 获取项目名的目录(因为我的当前文件是在项目名下的文件夹下的文件.所以是../)
sys.path.append(pwd+"../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AmazonProductsScout.settings")

import django
django.setup()

from product.models import Product


#获取上架时间
def get_date_first_available(selector):
    xpath_arrs = [
        '//span[contains(*,"Date First Available")]//text()',
        '//tr[contains(*,"Date First Available")]//text()'
    ]
    replace_strs = ['\n',':','Date First Available','                                 ','\u200e','\u200f']
    for xpath_arr in xpath_arrs:
        up_date = selector.xpath(xpath_arr)
        if len(up_date) > 0 :
            up_date = ''.join(up_date)
            for replace_str in replace_strs:
                up_date = up_date.replace(replace_str,'').strip()
            return up_date.strip()
    return ''

#获取排名rank
def get_product_rank(selector):
    xpath_arrs = [
        '//span[contains(*,"Best Sellers Rank")]//text()',
        '//tr[contains(*,"Best Sellers Rank")]//text()'
    ]
    replace_strs = ['\n','Best Sellers Rank',':']
    for xpath_arr in xpath_arrs:
        rank_text = selector.xpath(xpath_arr)
        if len(rank_text) > 0 :
            rank_text = ''.join(rank_text).split('(See')[0]
            for replace_str in replace_strs:
                rank_text = rank_text.replace(replace_str,'').strip()
            rank_text = rank_text.split(' in ')
            rank = rank_text[0].replace('#','').replace(',','')
            cat = rank_text[1]
            return rank.strip(),cat.strip()
    return 999999,'#NA'

page_start = 1 #首页
page_end = 100 #尾页

review_count = 300 #小于300
up_year = 2021 #上架时间在2021后
set_rank = 50000 #在大类目50000名内
filter_words_in_title = ['Mask','Masks'] #过滤标题关键词，如口罩
filter_cat = ['Amazon Launchpad'] #过滤类目输出结果
pool = ThreadPoolExecutor(max_workers=8)
has_crawled_asins = set()
cat_urls = [
    'https://www.amazon.com/s?i=garden&bbn=1055398&rh=n%3A1055398%2Cp_36%3A-3000&dc&fs=true&page={0}&qid=1652971610&rnid=386465011&ref=sr_pg_{1}',
    #'https://www.amazon.com/s?k=made+in+usa&i=kitchen&rh=n%3A284507&dc&page={0}&crid=29NW53ZKVYBMP&qid=1652338068&rnid=2941120011&sprefix=made+in+usa%2Caps%2C565&ref=sr_pg_{1}',
    'https://www.amazon.com/s?i=garden&bbn=1063498&rh=n%3A1055398%2Cn%3A3610841%2Cp_36%3A-3000&dc&fs=true&page={0}&qid=1652972061&rnid=1063498&ref=sr_pg_{1}',
    #'https://www.amazon.com/s?i=garden&bbn=1063498&rh=n%3A1055398%2Cn%3A3206325011%2Cp_36%3A-3000&dc&fs=true&page={0}&qid=1652972835&rnid=1063498&ref=sr_pg_{1}',
    #'https://www.amazon.com/s?i=garden&bbn=1063498&rh=n%3A1055398%2Cn%3A284507%2Cp_36%3A-3000&dc&fs=true&page={0}&qid=1652972883&rnid=1063498&ref=sr_pg_{1}',

]

#获取产品详情的线程：
def get_product_detail_worker(product_detail):
    scraper1 = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True,
            # 'mobile': True,
        }
    )
    product_detail_res = scraper1.get('https://www.amazon.com/dp/' + product_detail[0])
    product_detail_selector = etree.HTML(product_detail_res.text)
    date_first_available = get_date_first_available(product_detail_selector)
    rank, cat = get_product_rank(product_detail_selector)
    #print(threading.current_thread().name,[asin,date_first_available,cat])
    return [product_detail[0],product_detail[1],product_detail[2],date_first_available,rank,cat,product_detail[3],product_detail[4]]
#处理回调函数，产品详情
def get_product_detail_result(future):
    future_arr = future.result()
    asin = future_arr[0]
    price = future_arr[1]
    review_counts = future_arr[2]
    date_first_available = future_arr[3]
    rank = future_arr[4]
    cat = future_arr[5]
    title = future_arr[6]
    page = future_arr[7]
    data1 = [asin, date_first_available, rank, cat, review_counts, price, page]
    print(threading.current_thread().name,data1)
    if cat not in filter_cat:

        if date_first_available.find(',') != -1:
            year = date_first_available.split(',')[-1]
            if int(year) >= up_year and int(rank) < 50000:
                data = ['https://www.amazon.com/dp/' + asin,date_first_available,rank,cat, title, review_counts, price]
                print(data)
                p = Product()
                p.title = title
                p.asin = asin
                p.price = price
                p.rank = rank
                p.cat = cat
                p.review_counts = review_counts
                p.save()



for cat_url in cat_urls:
    for page in range(page_start,page_end):
        url = cat_url.format(page,page-1)
        #print(url)
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'linux',
                'desktop': True,
                # 'mobile': True,

            }
        )
        res = scraper.get(url)
        print('第%s页打开中...'%str(page),res.status_code)

        selector = etree.HTML(res.text)
        products_eles = selector.xpath('//div[@data-component-type="s-search-result"]')
        for products_ele in products_eles:
            texts = ''.join(products_ele.xpath('.//text()'))
            if texts.find('You’re seeing this ad based on the produc') != -1:
                continue
            title = ''.join(products_ele.xpath('.//span[@class="a-size-base-plus a-color-base a-text-normal"]/text()'))
            #剔除过滤的关键词
            filter_word_flag = 0
            for filter_word_in_title in filter_words_in_title:
                if texts.find(filter_word_in_title) != -1: #剔除口罩关键词
                    filter_word_flag = 1
                    break
            if filter_word_flag:
                continue

            reviews = ''.join(products_ele.xpath('.//span[@class="a-size-base s-underline-text"]/text()')).replace(',','')
            price = ''.join(products_ele.xpath('.//span[@class="a-price"]/span/text()')).replace('$','')
            asin = ''.join(products_ele.xpath('./@data-asin'))
            #print(asin,price,reviews)

            if reviews == '':
                reviews = '0'

            if int(reviews) < review_count:
                if asin not in has_crawled_asins: #提前单轮抓取过滤asin
                    has_crawled_asins.add(asin)
                    future1 = pool.submit(get_product_detail_worker, [asin,price,reviews,title,page])
                    future1.add_done_callback(get_product_detail_result)
        #time.sleep(2)





pool.shutdown()


