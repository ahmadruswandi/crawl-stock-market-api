# Generated by Django 2.1 on 2018-08-18 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawl', '0003_auto_20180819_0205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyinfo',
            name='ticker_symbol',
            field=models.CharField(max_length=6),
        ),
    ]
