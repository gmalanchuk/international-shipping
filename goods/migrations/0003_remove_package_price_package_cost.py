# Generated by Django 5.0.6 on 2024-07-09 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0002_package_article_package_delivery_cost_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='package',
            name='price',
        ),
        migrations.AddField(
            model_name='package',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=9, verbose_name='Стоимость'),
            preserve_default=False,
        ),
    ]
