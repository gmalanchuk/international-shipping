import logging

import django_filters

from goods.models import Package, Type

logger = logging.getLogger(__name__)


class DeliveryCostAndTypeFilter(django_filters.FilterSet):
    """Фильтрация по наличию стоимости доставки и типу посылки"""

    delivery_cost = django_filters.BooleanFilter(method='filter_has_delivery_cost')
    type = django_filters.ModelChoiceFilter(queryset=Type.objects.all())

    class Meta:
        model = Package
        fields = ('delivery_cost', 'type')

    def filter_has_delivery_cost(self, queryset, _, value):
        if value:  # если value == True, то возвращаются посылки с рассчитанной стоимостью доставки
            logger.debug("Returning packages with calculated delivery cost")
            return queryset.exclude(delivery_cost__isnull=True)
        else:  # если value == False, то возвращаются посылки без рассчитанной стоимости доставки
            logger.debug("Returning packages without calculated delivery cost")
            return queryset.filter(delivery_cost__isnull=True)
