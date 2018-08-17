from django.db import models

class Company(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    ticker_symbol = models.CharField(max_length=6, unique=True)
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=50)
    business = models.CharField(max_length=50)
    listing_bourse = models.CharField(max_length=10)
    crawled_at = models.DateTimeField(null=False, auto_created=True, auto_now=True)


