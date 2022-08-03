from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from lxml import etree
import re,time
from datetime import datetime,timedelta
from product.models import Product,SellerBase,Url
from django.utils import timezone
import redis
from django.conf import settings
import json

#过滤关注的类目
FILTER_CAT = ['Home & Kitchen','Health & Household','Automotive','Tools & Home Improvement','Kitchen & Dining']

def get_list_url(request):
    urls = Url.objects.all().order_by("id")
    ret_urls = []
    if len(urls) > 0:
        for url in urls:
            if url.start_page < url.end_page:
                start_url = url.start_url
                url_id = url.id
                start_page = url.start_page
                end_page = url.end_page
                for page in range(start_page,end_page+1):
                    ret_url = start_url.replace('<page>',str(page)).replace("<pre_page>",str(page-1))
                    ret_urls.append({"url":ret_url,"current_page":page})
                    if len(ret_urls) >= settings.URL_COUNT:
                        break

                #print(url.id,ret_urls)
                return HttpResponse(
                    json.dumps({"msg": 1, "urls": ret_urls, "url_id": url_id}))
            elif (timezone.now() - url.add_time).days >= 3:
                ##已经抓取完了，看需不需要重新抓取？
                url.start_page = 1
                url.add_time = timezone.now() #更新保存的时间
                url.save()
                return HttpResponse(json.dumps({"msg": 2})) #需要采集器刷新
    return HttpResponse(json.dumps({"msg":0}))



#获取采集卖家id的产品asins
#/product/get_seller_asins
def get_seller_asins(request):
    asins_ret = settings.REDIS_CONN.srandmember(settings.SELLER_WAIT,number=settings.URL_COUNT)
    if len(asins_ret) > 0:
        return HttpResponse(json.dumps({"msg":1,"asins":[i.decode() for i in asins_ret]}))
    else:
        return HttpResponse(json.dumps({"msg":0,"asins": ""}))

#获取采集卖家id的产品asins
#/product/get_product_asins
def get_product_asins(request):
    asins_ret = settings.REDIS_CONN.zrange(settings.PRODUCT_WAIT,0,settings.URL_COUNT)
    if len(asins_ret) > 0:
        return HttpResponse(json.dumps({"msg":1,"asins":[i.decode() for i in asins_ret]}))
    else:
        return HttpResponse(json.dumps({"msg":0,"asins": ""}))


#保存采集卖家id的产品asins到redis,不关注是否已经采集过url
#/product/add_seller_asins
def add_seller_asins(request):
    data = json.loads(request.body.decode("utf-8"))
    asins = data['asins']
    url_id = data['url_id']
    current_page = data['current_page']
    if asins != '':
        asin_arr = [asin for asin in asins.split("|")]
        #加入抓取卖家id的asin队列，先过滤再加入
        ex_rets = settings.REDIS_BL.bfMExists(settings.SELLER_FILTER, *(i for i in asin_arr))
        noex_asins = []
        for item in zip(ex_rets,asin_arr):
            if item[0] == 0:
                noex_asins.append(item[1])

        #print("ex_rets",ex_rets)
        #print("noex_asins",noex_asins)

        pipe = settings.REDIS_CONN.pipeline()
        for asin in noex_asins:
            pipe.sadd(settings.SELLER_WAIT, asin)
        ret = pipe.execute()
        #print("ret保存：", ret)
        if url_id != "" and current_page != '':
            r = Url.objects.get(id=url_id)
            r.start_page = current_page
            r.save()
        return HttpResponse(json.dumps({"msg":1}))
    else:
        return HttpResponse(json.dumps({"msg": 0}))

#保存采集卖家id的产品asins到redis,当前asin有关联产品时，继续添加到待爬队列
#/product/add_seller_re_asins
def add_seller_re_asins(request):
    data = json.loads(request.body.decode("utf-8"))
    asins = data['asins']
    if asins != '':
        asin_arr = [asin for asin in asins.split("|")]
        #加入抓取卖家id的asin队列，先过滤再加入
        ex_rets = settings.REDIS_BL.bfMExists(settings.SELLER_FILTER, *(i for i in asin_arr))
        noex_asins = []
        for item in zip(ex_rets,asin_arr):
            if item[0] == 0:
                noex_asins.append(item[1])
        #print("noex_asins保存：", noex_asins)
        pipe = settings.REDIS_CONN.pipeline()
        for asin in noex_asins:
            pipe.sadd(settings.SELLER_WAIT, asin)
        ret = pipe.execute()
        #print("ret保存：", ret)

        return HttpResponse(json.dumps({"msg":1}))
    else:
        return HttpResponse(json.dumps({"msg": 0}))




#保存产品asins到redis,不关注是否已经采集过url
#/product/add_product_asins
def add_product_asins(request):
    data = json.loads(request.body.decode("utf-8"))
    asins = data['asins']
    url_id = data['url_id']
    current_page = data['current_page']
    #print(request,asins,current_url)
    #加入待采集前，需要把过期的asin里面删除掉
    yesterday_score = int(time.mktime((datetime.now() + timedelta(days=-settings.ASIN_EXPIRE_DAY)).timetuple()))
    settings.REDIS_CONN.zremrangebyscore(settings.PRODUCT_FILTER, 0, yesterday_score)

    if asins != '':
        asin_arr = [asin for asin in asins.split("|")]
        #print(asin_arr)
        #加入抓取卖家id的asin队列，先过滤再加入
        pipe = settings.REDIS_CONN.pipeline()
        for asin in asin_arr:
            pipe.zrank(settings.PRODUCT_FILTER,asin)
        ex_rets = pipe.execute()
        noex_asins = []
        for item in zip(ex_rets,asin_arr):
            if item[0] == None:
                noex_asins.append(item[1])
        #print("noex_asins",noex_asins)
        pipe = settings.REDIS_CONN.pipeline()
        for asin in noex_asins:
            today_score = int(time.mktime(datetime.now().timetuple()))
            pipe.zadd(settings.PRODUCT_WAIT,{asin:today_score}, nx=True, ch=True) #加进去待采集队列，score为当前时间戳
        pipe.execute()


    #更新列表list信息
    if url_id != "" and current_page != '':
        r = Url.objects.get(id=url_id)
        r.start_page = current_page
        r.save()
    return HttpResponse(json.dumps({"msg":1}))

#保存采集到的seller_id到数据库
#/product/add_product_asins
def add_seller_info(request):
    data = json.loads(request.body.decode("utf-8"))
    data_ret = data['ret']
    asin = data['asin']
    if data_ret in [0,2]:  #404的asin返回
        settings.REDIS_BL.bfMAdd(settings.SELLER_FILTER, asin)
        settings.REDIS_CONN.srem(settings.SELLER_WAIT, asin)
        return HttpResponse(json.dumps({"msg": 0,"ret":data_ret}))

    if asin != '' and data_ret == 1:
        seller_id = data["seller_id"]
        SellerBase.objects.get_or_create(seller_id=seller_id)
        settings.REDIS_CONN.srem(settings.SELLER_WAIT, asin)
        return HttpResponse(json.dumps({"msg": 1, 'ret': data_ret}))

def product_content_post(request):
    data = json.loads(request.body.decode("utf-8"))
    data_ret = data['ret']
    asin = data['asin']
    if data_ret == 2:  #404的asin返回
        settings.REDIS_CONN.zrem(settings.PRODUCT_WAIT,asin)
        return HttpResponse(json.dumps({"msg": 0}))

    #print("asin",asin)

    seller_id = data["seller_id"]
    seller, b = SellerBase.objects.get_or_create(seller_id=seller_id)
    title = data['title']
    try:
        image = data['image']
    except Exception as e:
        image = ''
    price = data['price'].replace("$","").replace("US","")
    desc = data['desc']

    desc = desc.replace("\u200e",'')
    desc = desc.replace("\u200e",'')

    #print(desc)

    product_dimensions = '#NA'
    weight = '#NA'
    date_first_available = datetime.strptime("January 01, 1990", '%B %d, %Y')
    rank = 999999
    cat = '#NA'
    review_counts = 0
    ratings = 0

    items = desc.split("|")

    for item in items:

        if item.find('Package Dimensions') != -1:
            if item.find(';') != -1:
                product_dimensions = item.split(";")[0].replace("Package Dimensions",'').strip()
                weight = item.split(";")[1][1].strip()
            else:
                product_dimensions = item.replace("Package Dimensions",'').strip()
        if item.find('Item Weight') != -1:
            weight = item.replace('Item Weight','').strip()
        if item.find('Date First Available') != -1:
            date_first_available = item.replace("Date First Available",'').strip()
            date_first_available = datetime.strptime(date_first_available, '%B %d, %Y')
        if item.find('ASIN') != -1:
            asin = item.replace("ASIN",'').strip()
        if item.find('Best Sellers Rank') != -1:
            rank = item.replace("Best Sellers Rank","").split(' in ')[0].replace('#', '').replace(',', '').strip()
            cat = item.replace("Best Sellers Rank","").split(' in ')[-1].replace("(","").strip()
        if item.find('Customer Reviews') != -1:
            review_counts = item.replace("Customer Reviews","").split('out of 5 stars')[-1].replace("ratings","").replace("rating","").replace("Reviews","").replace("Review","").replace(',', '').strip()
            ratings = item.replace("Customer Reviews","").split('out of 5 stars')[0].strip()

    if review_counts == '':
        review_counts = 0
    if ratings == '':
        ratings = 0

    if rank == '':
        rank = 999999

    print([product_dimensions, weight, date_first_available, asin, rank,cat, review_counts, ratings])

    defaults = {
        'seller':seller,
        'title':title,
        'price':price,
        'image':image,
        'product_dimensions':product_dimensions,
        'weight':weight,
        'date_first_available':date_first_available,
        'last_rank':rank,
        'last_review_count':review_counts,
        'ratings':ratings,
        'cat':cat,

    }
    asin = data['asin']
    #print('asin2:',asin)
    if asin != "": #ret为0，1都要删除asin的key
        settings.REDIS_CONN.zrem(settings.PRODUCT_WAIT,asin)

    if cat != "#NA" and cat in FILTER_CAT and  data_ret == 1:
        p,b = Product.objects.get_or_create(asin=asin,defaults=defaults)
        print("查找结果：",p,b)
        if b == False:
            day = (timezone.now() - p.mod_time).days
            print(asin,p.mod_time,day)
            if day >= 1:
                p2,b2 = Product.objects.update_or_create(defaults=defaults,asin=asin)
                print("更新结果：",b2)

        return HttpResponse(json.dumps({"msg":1}))
    else:
        return HttpResponse(json.dumps({"msg":0}))