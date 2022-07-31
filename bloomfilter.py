# 自己的简单使用
from redisbloom.client import Client,Pipeline
import redis
from datetime import datetime,timedelta

import time
PRODUCT_WAIT = "product_wait" #产品监控采集等待队列，储存asin码，过滤reveiw，rank和上架日期
PRODUCT_FILTER = 'product_filter' #产品监控已采集过滤，redis zset，需要设置过期时间 1天

SELLER_WAIT = "seller_wait" #卖家id信息采集等待队列，
SELLER_FILTER = 'seller_filter' #采集卖家id时用，过滤用，不删除


REDIS_IP = '106.54.94.94'
REDIS_PORT = 6379
REDIS_PWD = 'foobared123'
REDIS_POOL = redis.ConnectionPool(host=REDIS_IP, port=REDIS_PORT,password=REDIS_PWD,db=0)
REDIS_CONN = redis.Redis(connection_pool= REDIS_POOL)
pipe = REDIS_CONN.pipeline()


yesterday_score = int(time.mktime((datetime.now() + timedelta(days=-1)).timetuple()))
today_score = int(time.mktime(datetime.now().timetuple()))
asins =  ['B09TSGH54J', 'B0B18JBRXW', 'B09XF6NVC4', 'B09YLPFNGH', 'B09QHX2BZ5', 'B09YXB5T8T', 'B09WRY4TMH', 'B09WXLRD9B', 'B0B1VB6657', 'B0B27Y4W3P', 'B09YMJPJCK', 'B09XQR12FV', 'B09YXRSRC3', 'B09YGV41SS', 'B09VK9RYNM', 'B09V2JVWD9', 'B09Y5P5MRH', 'B0B1V628W7', 'B09SWCZW7M', 'B09Z281KSK', 'B09WTXGFMB', 'B09WQZS6JX', 'B0B19WY9MQ', 'B08X6FZDZM']

ret = REDIS_CONN.zrange(PRODUCT_WAIT,0,10)
print(ret)

asin = 'B09GFT2H75'

ret = REDIS_CONN.zrem(PRODUCT_WAIT,asin)
print('删除结果',ret)


# for asin in asins:
#     # ret = REDIS_CONN.sadd(SELLER_WAIT,asin)
#     # print(ret)
#     today_score = int(time.mktime(datetime.now().timetuple()))
#     pipe.zadd(PRODUCT_WAIT, {asin: today_score}, nx=True, ch=True)
#
# pipe.execute()


# ret2 = REDIS_CONN.zremrangebyscore(PRODUCT_FILTER,0,yesterday_score-5)
# print(ret,ret2,yesterday_score,today_score)

#
# ret1 = REDIS_BL.bfMAdd(DETSIL_URL_FILTER,*asins_ret1)
# asins_ret2 = (i.decode() for i in asins_ret)
# ret2 = REDIS_BL.bfMExists(DETSIL_URL_FILTER,*asins_ret2)
# print(ret1,ret2)




#
# # 因为我使用的是虚拟机中docker的redis, 填写虚拟机的ip地址和暴露的端口
# rb = Client(host='106.54.94.94', port=6379,password='foobared123')
# # rb.bfCreate('bloom', 0.01, 1000)
# #rb.cfCreate('urls', 1000000)
# #ret1 = rb.cfAdd('urls', 'filter')        # returns 1
# ret2 = rb.cfAddNX('urls', 'filter')      # returns 0
# ret3 = rb.cfExists('urls', 'filter')     # returns 1
# ret4 = rb.cfExists('urls', 'noexist')    # returns 0
# print(ret2,ret3,ret4)
# rb.cfDel('urls','filter')
# print(rb.cfExists('urls','filter'))

# import redis
# r = redis.Redis(host='106.54.94.94', port=6379,password='foobared123',db=0)
# ret = r.sadd('url','1','2','4')
# print(ret)
# ret = r.sadd('url','1')
# ret = r.sadd('url','苏章林')
# print(ret)
#
# counts = r.scard('url')
# print(counts)
#
# all_members = r.smembers('url')
# print(all_members)
# print(type(all_members))
# for i in all_members:
#     print(i,type(i),i.decode('utf-8'))

# print(r.srandmember('list_wait_queue').decode())
