# Generated by Django 3.2.13 on 2022-07-07 02:09

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='标题')),
                ('image', models.CharField(default='', max_length=500)),
                ('product_dimensions', models.CharField(default='', max_length=200, verbose_name='尺寸')),
                ('weight', models.CharField(default='', max_length=50, verbose_name='重量')),
                ('asin', models.CharField(default='', max_length=10, unique=True, verbose_name='ASIN')),
                ('price', models.FloatField(verbose_name='价格')),
                ('cat', models.CharField(default='', max_length=100, verbose_name='类目')),
                ('review_counts', models.IntegerField(verbose_name='评论数')),
                ('ratings', models.FloatField(default='5.0', verbose_name='评分')),
                ('date_first_available', models.DateField(default='1990-01-01', verbose_name='上架日期')),
                ('display', models.BooleanField(default=True, verbose_name='是否展示')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='保存日期')),
                ('mod_time', models.DateTimeField(auto_now=True, verbose_name='最后修改日期')),
            ],
        ),
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField(verbose_name='排名')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='保存日期')),
                ('mod_time', models.DateTimeField(auto_now=True, verbose_name='最后修改日期')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_counts', models.IntegerField(default=0, verbose_name='评论数')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='保存日期')),
                ('mod_time', models.DateTimeField(auto_now=True, verbose_name='最后修改日期')),
            ],
        ),
        migrations.CreateModel(
            name='SellerBase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(max_length=200, verbose_name='品牌名称')),
                ('seller_id', models.CharField(max_length=200, unique=True, verbose_name='卖家id')),
                ('business_name', models.CharField(default='', max_length=300, verbose_name='公司名称')),
                ('business_addr', models.CharField(default='', max_length=300, verbose_name='公司地址')),
                ('country', models.CharField(default='', max_length=10, verbose_name='所在国家')),
                ('display', models.BooleanField(default=True, verbose_name='是否跟踪')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='保存日期')),
                ('mod_time', models.DateTimeField(auto_now=True, verbose_name='最后修改日期')),
            ],
        ),
        migrations.CreateModel(
            name='SellerDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_counts', models.IntegerField(default=0, verbose_name='产品数')),
                ('days_30_ratings', models.IntegerField(default=0, verbose_name='30天fd数')),
                ('days_90_ratings', models.IntegerField(default=0, verbose_name='90天fd数')),
                ('year_ratings', models.IntegerField(default=0, verbose_name='一年fd数')),
                ('life_ratings', models.IntegerField(default=0, verbose_name='总fd数')),
                ('display', models.BooleanField(default=True, verbose_name='是否跟踪')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='保存日期')),
                ('mod_time', models.DateTimeField(auto_now=True, verbose_name='最后修改日期')),
                ('seller_base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.sellerbase')),
            ],
        ),
        migrations.AddIndex(
            model_name='sellerbase',
            index=models.Index(fields=['seller_id'], name='product_sel_seller__8bc9fa_idx'),
        ),
        migrations.AddField(
            model_name='review',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
        migrations.AddField(
            model_name='rank',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
        migrations.AddField(
            model_name='product',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.sellerbase'),
        ),
        migrations.AddIndex(
            model_name='sellerdetail',
            index=models.Index(fields=['seller_base'], name='product_sel_seller__a9e701_idx'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['product'], name='product_rev_product_b4e72e_idx'),
        ),
        migrations.AddIndex(
            model_name='rank',
            index=models.Index(fields=['product'], name='product_ran_product_627e2d_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['asin'], name='product_pro_asin_59c143_idx'),
        ),
    ]