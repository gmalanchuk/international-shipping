import asyncio
import logging
from decimal import Decimal

import aiohttp
from asgiref.sync import sync_to_async
from celery import shared_task
from django.core.cache import cache
from goods.models import Package

logger = logging.getLogger(__name__)


async def calculate_delivery_cost_async():
    """Рассчёт стоимости доставки для всех посылок, у которых она не указана. Рассчёт происходит каждые 5 минут"""

    try:
        # Достать курс доллара к рублю из кэша. Если курс доллара не содержится в кэше(истекает каждые 5 минут), то
        # сделать запрос к сайту ЦБ РФ и положить его в кэш
        dollar_to_ruble_exchange_rate = cache.get('dollar_to_ruble_exchange_rate')
        if not dollar_to_ruble_exchange_rate:
            url = 'https://www.cbr-xml-daily.ru/daily_json.js'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response = await response.json(content_type=None)
                    dollar_to_ruble_exchange_rate = response['Valute']['USD']['Value']
                    cache.set('dollar_to_ruble_exchange_rate', dollar_to_ruble_exchange_rate, timeout=60 * 5)
    except Exception as e:
        logger.error(f'Error during getting dollar to ruble exchange rate: {e}')
        return

    try:
        # Достать все посылки, у которых не указана стоимость доставки и рассчитать её
        packages = await sync_to_async(list)(Package.objects.filter(delivery_cost__isnull=True))
        for package in packages:
            package.delivery_cost = (package.weight * Decimal(0.5) + package.cost * Decimal(0.01)) * Decimal(dollar_to_ruble_exchange_rate)
        await sync_to_async(Package.objects.bulk_update)(packages, ['delivery_cost'])
    except Exception as e:
        logger.error(f'Error during updating delivery costs: {e}')
        return

    logger.info('Delivery costs updated successfully')


@shared_task
def calculate_delivery_cost():
    asyncio.run(calculate_delivery_cost_async())
