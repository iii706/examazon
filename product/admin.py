from django.contrib import admin
from django.utils.html import format_html
from product.models import Product,Rank,Review,SellerBase,SellerDetail,Url,UrlType

from django.contrib import admin

admin.site.site_title="亚马逊产品数据"
admin.site.site_header="亚马逊产品数据管理"
admin.site.index_title="欢迎登陆，选择以下信息进入："

#@admin.register(UrlType)
class UrlTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'url_type','comment']



@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    list_display = ['id', 'start_url', 'start_page', 'end_page', "page_replace_pattern", 'pre_page_replace_pattern','show_add_time','show_mod_time']


# Register your models here.
##修改后台某列列宽
class GuardedAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/guarded_admin.js',)




@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','IMAGE','title','price','cat',"last_rank",'last_review_count','add_date_first_available','show_mod_time']
    list_display_links = ['id'] #可以直接链接到编辑页面
    list_filter = ['cat']
    search_fields = ["title","asin"]

    def IMAGE(self,obj):
        return format_html("<a href='https://www.amazon.com/dp/{asin}' target='blank'><img src='{image}' width=150 ><br/></a>",asin=obj.asin, image=obj.image)

    IMAGE.short_description = "产品详情"






@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ['id','product','rank','show_add_time','show_mod_time']
    search_fields = ["product__title","product__asin"]  ##外键search_fields需要双下划线


@admin.register(SellerBase)
class SellerBaseAdmin(admin.ModelAdmin):
    list_display = ['id','SELL_LINK','brand_name','country','last_product_counts','last_days_30_ratings','last_days_90_ratings','last_year_ratings','last_life_ratings','show_add_time','show_mod_time']
    list_filter = ['country','display']

    def SELL_LINK(self,obj):
        return format_html("<a href='https://www.amazon.com/s?me={seller_id}&marketplaceID=ATVPDKIKX0DER' target='blank'>{seller_id}</a>",seller_id=obj.seller_id)

    SELL_LINK.short_description = "卖家链接"


@admin.register(Review)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ['id','product','review_counts','show_add_time','show_mod_time']

@admin.register(SellerDetail)
class SellerDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'seller_base', 'product_counts', 'days_30_ratings', 'days_90_ratings', 'year_ratings', 'life_ratings', 'show_add_time', 'show_mod_time']
    list_display_links = ['seller_base']  # 可以直接链接到编辑页面






