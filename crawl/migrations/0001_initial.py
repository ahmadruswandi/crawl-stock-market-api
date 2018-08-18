# Generated by Django 2.1 on 2018-08-18 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('crawled_at', models.DateTimeField(auto_created=True, auto_now=True)),
                ('id', models.IntegerField(auto_created=True, primary_key=True, serialize=False)),
                ('ticker_symbol', models.CharField(max_length=6, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('url', models.CharField(max_length=50)),
                ('business', models.CharField(max_length=50)),
                ('listing_bourse', models.CharField(max_length=10)),
                ('revenue', models.BigIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CompanyInfo',
            fields=[
                ('id', models.IntegerField(auto_created=True, primary_key=True, serialize=False)),
                ('ticker_symbol', models.CharField(max_length=6, unique=True)),
                ('param_name', models.CharField(max_length=50)),
                ('param_value', models.CharField(max_length=600)),
            ],
        ),
    ]
