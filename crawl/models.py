from django.db import models

class Company(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    ticker_symbol = models.CharField(max_length=6, unique=True)
    name = models.CharField(max_length=150)
    url = models.CharField(max_length=150)
    business = models.CharField(max_length=150)
    listing_bourse = models.CharField(max_length=10)
    revenue = models.BigIntegerField(null=True)
    crawled_at = models.DateTimeField(null=False, auto_created=True, auto_now=True)

class CompanyInfo(models.Model):
    ticker_symbol = models.CharField(max_length=6)
    param_name = models.CharField(max_length=50)
    param_value = models.CharField(max_length=600)

    class Meta:
        unique_together = ('ticker_symbol', 'param_name',)


