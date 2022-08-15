from django.contrib import admin
from django.utils.html import format_html
from product.models import Product,Rank,Review,SellerBase,SellerDetail,Url,UrlType

from django.contrib import admin



admin.site.site_title="亚马逊产品数据"
admin.site.site_header="亚马逊产品数据管理"
admin.site.index_title="欢迎登陆，选择以下信息进入："

#from django.utils.translation import ugettext_lazy as _

from django.utils.translation import gettext_lazy as _



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

    class Media:
        js = (
            'js/product_admin.js',  # project static folder
        )




@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ['id','product','rank','show_add_time','show_mod_time']
    search_fields = ["product__title","product__asin"]  ##外键search_fields需要双下划线


@admin.register(SellerBase)
class SellerBaseAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(display=True).exclude(country='CN')


    def pass_audit_str(self,obj):
        parameter_str = 'id={}'.format(str(obj.id))
        color_code = ''
        btn_str = '<span class="btn btn-xs btn-danger myspan_select" href="{}" title="123">' \
                  '<input name="不再关注"' \
                  'type="button" id="passButton" ' \
                  'title="passButton" value="不再关注">' \
                  '</span>'
        #return format_html(btn_str, '/pass_audit/?{}'.format(parameter_str))
        return format_html(btn_str,'')

    pass_audit_str.short_description = '操作'



    class CountryListFilter(admin.SimpleListFilter):
        title = _(u'卖家所在国家')
        parameter_name = 'country'

        def lookups(self, request, model_admin):
            return (
                ('0', _(u'中国卖家')),
                ('1', _(u'非中国卖家')),
            )

        def queryset(self, request, queryset):
            if self.value() == '0':
                return queryset.filter(country='CN')
            if self.value() == '1':
                return queryset.filter().exclude(country='CN')

    list_display = ['id','SELL_LINK','pass_audit_str','brand_name','country','last_product_counts','last_days_30_ratings','last_days_90_ratings','last_year_ratings','last_life_ratings','show_add_time','show_mod_time']
    # 激活自定义过滤器
    #list_filter = (CountryListFilter,)

    def SELL_LINK(self,obj):
        return format_html("<a href='https://www.amazon.com/s?me={seller_id}&marketplaceID=ATVPDKIKX0DER' target='blank'>{seller_id}</a>",seller_id=obj.seller_id)

    SELL_LINK.short_description = "卖家链接"

    class Media:
        js = (
            'js/guarded_admin.js',  # project static folder
        )


@admin.register(Review)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ['id','product','review_counts','show_add_time','show_mod_time']

@admin.register(SellerDetail)
class SellerDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'seller_base', 'product_counts', 'days_30_ratings', 'days_90_ratings', 'year_ratings', 'life_ratings', 'show_add_time', 'show_mod_time']
    list_display_links = ['seller_base']  # 可以直接链接到编辑页面






