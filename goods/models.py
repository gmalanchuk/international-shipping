import uuid

from django.db import models


def generate_article():
    return str(uuid.uuid4()).replace('-', '')[:10]


class Package(models.Model):
    name = models.CharField(max_length=100)
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    type = models.ForeignKey('Type', on_delete=models.CASCADE)
    article = models.CharField(default=generate_article, max_length=10)   # индивидуальный айди посылки
    delivery_cost = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=52)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
