# Generated by Django 4.0.5 on 2022-07-15 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_rename_url_type_url_urltype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='url',
            name='start_url',
            field=models.CharField(max_length=500, verbose_name='初始链接地址'),
        ),
    ]
