from django.urls import path
from . import views
#假如一个项目中有大量的应用，那就要用以命名空间，防止有相同的url分别不清
app_name = 'product' #模板中用： product:detail
urlpatterns = [
    path('post/',views.product_content_post,name='detail'),
    path('get_seller_asins/',views.get_seller_asins,name='get_seller_asins'),
    path('add_seller_asins/',views.add_seller_asins,name='add_seller_asins'),
    path('add_seller_re_asins/',views.add_seller_re_asins,name='add_seller_re_asins'), #关联asin增加
    path('add_seller_info/',views.add_seller_info,name='add_seller_info'),
    path('get_product_asins/',views.get_product_asins,name='get_product_asins'),
    path('add_product_asins/',views.add_product_asins,name='add_product_asins'),
    path('get_list_url/',views.get_list_url,name='get_list_url'),
]