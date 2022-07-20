from django.db import models
from django.contrib import admin
# Create your models here.
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils import timezone
from redisbloom.client import Client
from django.conf import settings
#Url类型
class UrlType(models.Model):
    url_type = models.CharField(verbose_name="url类型", max_length=20, default="cat")
    comment = models.CharField(verbose_name="备注", max_length=20,default="")
    def __str__(self):
        return self.url_type +'|'+self.comment
    class Meta:
        verbose_name = "抓取链接类型"
        verbose_name_plural = verbose_name  # admin不显示s复数


#初始Url链接
class Url(models.Model):
    start_url = models.CharField(verbose_name="初始链接地址",max_length=500)
    start_page = models.IntegerField(verbose_name="开始页数",default=1)
    end_page = models.IntegerField(verbose_name="结束页数",default=200)
    page_replace_pattern = models.CharField(verbose_name="上一页替换字符",max_length=10,default="<page>")
    pre_page_replace_pattern = models.CharField(verbose_name="上一页替换字符",max_length=20,default="<pre_page>")
    urltype = models.ForeignKey("UrlType", on_delete=models.CASCADE)
    add_time = models.DateTimeField("保存日期", default=timezone.now)
    mod_time = models.DateTimeField("最后修改日期", auto_now=True)
    def show_add_time(self):
        return self.add_time.strftime('%Y-%m-%d %H:%M:%S')
    show_add_time.admin_order_field = 'add_time'
    show_add_time.short_description = '添加时间'


    def show_mod_time(self):
        return self.mod_time.strftime('%Y-%m-%d %H:%M:%S')
    show_mod_time.admin_order_field = 'add_time'
    show_mod_time.short_description = '最后修改时间'


    # def save(self, *args, **kwargs):
    #     super(Url, self).save(*args, **kwargs)
    #     pipe = settings.REDIS_CONN.pipeline()
    #     for page in range(self.start_page,self.end_page):
    #         url = self.start_url.replace(self.page_replace_pattern,str(page)).replace(self.pre_page_replace_pattern,str(page-1))
    #         pipe.sadd(settings.LIST_URL_QUEUE,url)
    #     pipe.execute()

    class Meta:
        verbose_name = "抓取链接信息"
        verbose_name_plural = verbose_name  # admin不显示s复数


#关键词信息表
class Word(models.Model):
     word_content = models.CharField(verbose_name="关键词",max_length=200)
     search_month_vol = models.IntegerField(verbose_name="月搜索量",default=0)
     search_3m_vol = models.IntegerField(verbose_name="3月搜索量",default=0)
     search_12m_vol = models.IntegerField(verbose_name="年均搜索量",default=0)
     search_rank = models.IntegerField(verbose_name="词排名",default=9999999)
     search_product_results = models.IntegerField(verbose_name="搜索产品总数",default=0)
     search_products_review_counts = models.IntegerField(verbose_name="搜索产品总评论数",default=0)
     product = models.ManyToManyField('Product',through='WordShip') #关联产品,through自定义中间表
     add_time = models.DateTimeField("保存日期", default=timezone.now)
     mod_time = models.DateTimeField("最后修改日期", auto_now=True)

     class Meta:
         indexes = [
             models.Index(fields=["word_content", "search_rank"])
         ]
         verbose_name = "关键词"
         verbose_name_plural = verbose_name #admin不显示s复数

     def show_add_time(self):
         return self.add_time.strftime('%Y-%m-%d %H:%M:%S')

     show_add_time.admin_order_field = 'add_time'
     show_add_time.short_description = '抓取时间'

     def show_mod_time(self):
         return self.mod_time.strftime('%Y-%m-%d %H:%M:%S')

     show_mod_time.admin_order_field = 'add_time'
     show_mod_time.short_description = '最后修改时间'

#搜索词跟产品之间的关联表
class WordShip(models.Model):
    word = models.ForeignKey("Product", on_delete=models.CASCADE)
    product = models.ForeignKey("Word", on_delete=models.CASCADE)
    search_persent = models.FloatField(verbose_name="搜索占比")
    add_time = models.DateTimeField("保存日期", default=timezone.now)
    mod_time = models.DateTimeField("最后修改日期", auto_now=True)
    class Meta:
        indexes = [
            models.Index(fields=["word","product"])
        ]
        verbose_name = "关键词关联数据"
        verbose_name_plural = verbose_name  # admin不显示s复数

    def show_add_time(self):
        return self.add_time.strftime('%Y-%m-%d %H:%M:%S')

    show_add_time.admin_order_field = 'add_time'
    show_add_time.short_description = '抓取时间'

    def show_mod_time(self):
        return self.mod_time.strftime('%Y-%m-%d %H:%M:%S')

    show_mod_time.admin_order_field = 'add_time'
    show_mod_time.short_description = '最后修改时间'


#产品信息表
class Product(models.Model):
    seller = models.ForeignKey('SellerBase', on_delete=models.CASCADE)
    title = models.CharField(verbose_name="标题",max_length=500)
    image = models.CharField(max_length=500,default='')
    product_dimensions = models.CharField(verbose_name="尺寸",max_length=200,default='')
    weight = models.CharField(verbose_name="重量",max_length=50,default='')
    asin = models.CharField(verbose_name="ASIN",max_length=10,default='',unique = True,null=False) #'https://www.amazon/dp/asin'
    price = models.FloatField(verbose_name="价格")
    last_rank = models.IntegerField(verbose_name="最新排名",default=999999)
    last_review_count = models.IntegerField(verbose_name="最新评论数",default=0)
    cat = models.CharField(verbose_name="类目", max_length=100, default='')
    ratings = models.FloatField(verbose_name="评分",default='5.0')
    date_first_available = models.DateField(verbose_name="上架日期",default='1990-01-01')
    display = models.BooleanField(verbose_name="是否展示",default=True)
    add_time = models.DateTimeField("保存日期",default = timezone.now)
    mod_time = models.DateTimeField("最后修改日期",auto_now = True)

    def add_date_first_available(self):
        return self.date_first_available.strftime('%Y-%m-%d')
    add_date_first_available.admin_order_field = "date_first_available"
    add_date_first_available.short_description = "上架日期"

    def __str__(self):
        return self.asin +'|'+self.title[:20]

    class Meta:
        indexes = [
            models.Index(fields=["asin"])
        ]
        verbose_name = "产品基础数据"
        verbose_name_plural = verbose_name  # admin不显示s复数

    def show_add_time(self):
        return self.add_time.strftime('%Y-%m-%d %H:%M:%S')

    show_add_time.admin_order_field = 'add_time'
    show_add_time.short_description = '抓取时间'

    def show_mod_time(self):
        return self.mod_time.strftime('%Y-%m-%d %H:%M:%S')

    show_mod_time.admin_order_field = 'add_time'
    show_mod_time.short_description = '最后修改时间'

    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)
        r = Rank()
        r.product = self
        r.rank = self.last_rank
        r.save()

        review = Review()
        review.review_counts = self.last_review_count
        review.product = self
        review.save()

#排名信息表
class Rank(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    rank = models.IntegerField(verbose_name="排名")
    add_time = models.DateTimeField("保存日期", default=timezone.now)
    mod_time = models.DateTimeField("最后修改日期", auto_now=True)
    class Meta:
        indexes = [
            models.Index(fields=["product"])
        ]

        verbose_name = "产品排名数据"
        verbose_name_plural = verbose_name  # admin不显示s复数

    def show_add_time(self):
        return self.add_time.strftime('%Y-%m-%d %H:%M:%S')

    show_add_time.admin_order_field = 'add_time'
    show_add_time.short_description = '抓取时间'

    def show_mod_time(self):
        return self.mod_time.strftime('%Y-%m-%d %H:%M:%S')

    show_mod_time.admin_order_field = 'add_time'
    show_mod_time.short_description = '最后修改时间'


#卖家信息表
class SellerBase(models.Model):
    def save(self,*args, **kwargs):
        super(SellerBase,self).save(*args, **kwargs)
        seller_detail = SellerDetail()
        seller_detail.seller_base = self
        seller_detail.days_30_ratings = self.last_days_30_ratings
        seller_detail.days_90_ratings = self.last_days_90_ratings
        seller_detail.year_ratings = self.last_year_ratings
        seller_detail.life_ratings = self.last_life_ratings
        seller_detail.product_counts = self.last_product_counts
        seller_detail.save()

    def __str__(self):
        return self.seller_id


    brand_name = models.CharField(verbose_name="品牌名称",max_length=200)
    seller_id = models.CharField(verbose_name="卖家id",max_length=200,unique = True,null=False)
    business_name = models.CharField(verbose_name="公司名称",max_length=300,default='')
    business_addr = models.CharField(verbose_name="公司地址",max_length=300,default='')
    last_product_counts = models.IntegerField(verbose_name="产品数", default=0)
    last_days_30_ratings = models.IntegerField(verbose_name="30天fd数", default=0)
    last_days_90_ratings = models.IntegerField(verbose_name="90天fd数", default=0)
    last_year_ratings = models.IntegerField(verbose_name="一年fd数", default=0)
    last_life_ratings = models.IntegerField(verbose_name="总fd数", default=0)
    country = models.CharField(verbose_name="所在国家",max_length=10,default='')
    display = models.BooleanField(verbose_name="是否跟踪", default=True)
    add_time = models.DateTimeField("保存日期", default=timezone.now)
    mod_time = models.DateTimeField("最后修改日期", auto_now=True)
    class Meta:
        indexes = [
            models.Index(fields=["seller_id"])
        ]
        verbose_name = "卖家基础信息"
        verbose_name_plural = verbose_name  # admin不显示s复数

    def show_add_time(self):
        return self.add_time.strftime('%Y-%m-%d %H:%M:%S')

    show_add_time.admin_order_field = 'add_time'
    show_add_time.short_description = '抓取时间'

    def show_mod_time(self):
        return self.mod_time.strftime('%Y-%m-%d %H:%M:%S')

    show_mod_time.admin_order_field = 'add_time'
    show_mod_time.short_description = '最后修改时间'

#卖家详细信息表
class SellerDetail(models.Model):
    seller_base = models.ForeignKey('SellerBase', on_delete=models.CASCADE)
    product_counts = models.IntegerField(verbose_name="产品数", default=0)
    days_30_ratings = models.IntegerField(verbose_name="30天fd数", default=0)
    days_90_ratings = models.IntegerField(verbose_name="90天fd数", default=0)
    year_ratings = models.IntegerField(verbose_name="一年fd数", default=0)
    life_ratings = models.IntegerField(verbose_name="总fd数", default=0)
    display = models.BooleanField(verbose_name="是否跟踪", default=True)
    add_time = models.DateTimeField("保存日期", default=timezone.now)
    mod_time = models.DateTimeField("最后修改日期", auto_now=True)
    class Meta:
        indexes = [
            models.Index(fields=["seller_base"])
        ]
        verbose_name = "卖家历史数据"
        verbose_name_plural = verbose_name  # admin不显示s复数

    def show_add_time(self):
        return self.add_time.strftime('%Y-%m-%d %H:%M:%S')

    show_add_time.admin_order_field = 'add_time'
    show_add_time.short_description = '抓取时间'

    def show_mod_time(self):
        return self.mod_time.strftime('%Y-%m-%d %H:%M:%S')

    show_mod_time.admin_order_field = 'add_time'
    show_mod_time.short_description = '最后修改时间'


#评论信息表
class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    review_counts = models.IntegerField(verbose_name="评论数",default=0)
    add_time = models.DateTimeField("保存日期", default=timezone.now)
    mod_time = models.DateTimeField("最后修改日期", auto_now=True)
    class Meta:
        indexes = [
            models.Index(fields=["product"])
        ]
        verbose_name = "产品评论数据"
        verbose_name_plural = verbose_name  # admin不显示s复数

    def show_add_time(self):
        return self.add_time.strftime ('%Y-%m-%d %H:%M:%S')
    show_add_time.admin_order_field = 'add_time'
    show_add_time.short_description = '抓取时间'

    def show_mod_time(self):
        return self.mod_time.strftime ('%Y-%m-%d %H:%M:%S')
    show_mod_time.admin_order_field = 'add_time'
    show_mod_time.short_description = '最后修改时间'