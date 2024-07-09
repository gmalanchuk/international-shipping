import asyncio
from decimal import Decimal

import aiohttp
from asgiref.sync import sync_to_async
from celery import shared_task
from django.core.cache import cache
from goods.models import Package


async def calculate_delivery_cost_async():
    dollar_to_ruble_exchange_rate = cache.get('dollar_to_ruble_exchange_rate')

    if not dollar_to_ruble_exchange_rate:
        url = 'https://www.cbr-xml-daily.ru/daily_json.js'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response = await response.json(content_type=None)
                dollar_to_ruble_exchange_rate = response['Valute']['USD']['Value']
                cache.set('dollar_to_ruble_exchange_rate', dollar_to_ruble_exchange_rate, timeout=60 * 5)

    packages = await sync_to_async(list)(Package.objects.filter(delivery_cost__isnull=True))
    for package in packages:
        package.delivery_cost = (package.weight * Decimal(0.5) + package.price * Decimal(0.01)) * Decimal(dollar_to_ruble_exchange_rate)

    await sync_to_async(Package.objects.bulk_update)(packages, ['delivery_cost'])

    print('проставлено')


@shared_task
def calculate_delivery_cost():
    asyncio.run(calculate_delivery_cost_async())
