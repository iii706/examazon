import cloudscraper
from datetime import datetime
import time,random
from lxml import etree

from concurrent.futures import ThreadPoolExecutor,as_completed,wait, FIRST_COMPLETED, ALL_COMPLETED
import threading
import time
import sys
import os

import django
pwd = os.path.dirname(os.path.realpath(__file__))
# 获取项目名的目录(因为我的当前文件是在项目名下的文件夹下的文件.所以是../)
sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AmazonProductsScout.settings")
django.setup()


from product.models import Product



        #time.sleep(2)
page_start = 1 #首页
page_end = 100 #尾页
ret = 1
review_count = 30000 #小于300
up_year = 2021 #上架时间在2021后
set_rank = 500000 #在大类目50000名内
filter_words_in_title = ['Mask','Masks'] #过滤标题关键词，如口罩
filter_cat = ['Amazon Launchpad'] #过滤类目输出结果
pool = ThreadPoolExecutor(max_workers=16)
pool2 = ThreadPoolExecutor(max_workers=4)
has_crawled_asins = set()
crawl_start = time.time()


cat_urls = [
    'https://www.amazon.com/s?i=garden&bbn=1055398&rh=n%3A1055398%2Cp_36%3A-3000&dc&fs=true&page={0}&qid=1652971610&rnid=386465011&ref=sr_pg_{1}',
    #'https://www.amazon.com/s?k=made+in+usa&i=kitchen&rh=n%3A284507&dc&page={0}&crid=29NW53ZKVYBMP&qid=1652338068&rnid=2941120011&sprefix=made+in+usa%2Caps%2C565&ref=sr_pg_{1}',
    'https://www.amazon.com/s?i=garden&bbn=1063498&rh=n%3A1055398%2Cn%3A3610841%2Cp_36%3A-3000&dc&fs=true&page={0}&qid=1652972061&rnid=1063498&ref=sr_pg_{1}',
    #'https://www.amazon.com/s?i=garden&bbn=1063498&rh=n%3A1055398%2Cn%3A3206325011%2Cp_36%3A-3000&dc&fs=true&page={0}&qid=1652972835&rnid=1063498&ref=sr_pg_{1}',
    #'https://www.amazon.com/s?i=garden&bbn=1063498&rh=n%3A1055398%2Cn%3A284507%2Cp_36%3A-3000&dc&fs=true&page={0}&qid=1652972883&rnid=1063498&ref=sr_pg_{1}',

]






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



#获取产品详情的线程：
def get_product_detail_worker(product_detail):
    start = time.time()
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
    end = time.time()
    take_time = end-start
    main_time = start - crawl_start
    print("单次用时：",take_time,main_time,product_detail[-1])
    datas = [threading.current_thread().name,product_detail[0],product_detail[1],product_detail[2],date_first_available,rank,cat,product_detail[3],product_detail[4]]
    return datas


def get_page_content(page):
    url = cat_urls[0].format(page, page - 1)
    # print(url)
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'linux',
            'desktop': True,
            # 'mobile': True,

        }
    )
    res = scraper.get(url)
    print('第%s页打开中...' % str(page), res.status_code)
    selector = etree.HTML(res.text)
    products_eles = selector.xpath('//div[@data-component-type="s-search-result"]')
    need_crawl_datas = []
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

        if asin not in has_crawled_asins: #提前单轮抓取过滤asin
            has_crawled_asins.add(asin)

            need_crawl_datas.append([asin,price,reviews,title[:50],page])
    print("需要采集长度：",len(need_crawl_datas))
    if len(need_crawl_datas) > 0:
        return need_crawl_datas

list_tasks = [pool2.submit(get_page_content,page) for page in range(page_start,page_end)]

for list_task in as_completed(list_tasks):
    need_crawl_datas = list_task.result()
    all_task = [pool.submit(get_product_detail_worker, i) for i in need_crawl_datas]
    for future in as_completed(all_task):
        print(future.result())


pool.shutdown()
pool2.shutdown()

