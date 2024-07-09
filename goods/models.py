import random
import string

from django.db import models


class Package(models.Model):
    """Модель посылки"""

    name = models.CharField(max_length=100, verbose_name='Название')
    weight = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Вес')
    cost = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Стоимость')
    type = models.ForeignKey(to='Type', on_delete=models.CASCADE, verbose_name='Тип посылки')
    article = models.CharField(unique=True, max_length=10, verbose_name='Уникальный номер посылки')
    delivery_cost = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True, verbose_name='Стоимость доставки')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ID: {self.pk} | Name: {self.name} | Article: {self.article}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Присвоение артикула только при создании объекта
            self.article = self.__generate_article_code()
        super().save(*args, **kwargs)

    def __generate_article_code(self):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=10))


class Type(models.Model):
    """Модель типа посылки (одежда, электроника и тд)"""

    name = models.CharField(max_length=52, verbose_name='Название')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ID: {self.pk} | Name: {self.name}"
