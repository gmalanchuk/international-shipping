import json
import logging
from urllib.parse import urlencode

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from goods.filters import DeliveryCostAndTypeFilter
from goods.models import Package, Type
from goods.serializers import TypeSerializer, PackageRetrieveListSerializer, PackageCreateSerializer


logger = logging.getLogger(__name__)


@extend_schema(tags=['Packages'])
class PackageViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageRetrieveListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = DeliveryCostAndTypeFilter

    def create(self, request, *args, **kwargs):
        """Метод создаёт посылку и сохраняет её уникальный артикул в сессию
        для того, чтобы пользователь мог просматривать свои посылки.
        (У пользователя нет возможности просматривать чужие посылки)"""

        response = super().create(request, *args, **kwargs)
        article = response.data['article']
        logger.info(f"Package created with article {article}")

        if 'articles' not in request.session:
            request.session['articles'] = []

        request.session['articles'].append(article)
        request.session.modified = True
        logger.debug(f"Article {article} added to session")

        return response

    def list(self, request, *args, **kwargs):
        """Получение списка посылок, которые были созданы пользователем.
        Также возможна фильтрация по типу посылки и факту наличия
        рассчитанной стоимости доставки"""

        # TODO вынести кеш в отдельный метод
        # Создание cache_key с учётом параметров запроса
        sorted_query_params = sorted(request.GET.items())
        query_string = urlencode(sorted_query_params, doseq=True)

        session_key = request.session.session_key
        cache_key = f"packages_list_{session_key}_{query_string}"
        cached_response = cache.get(cache_key)

        # Если ответ на запрос уже кеширован, то возвращаем его
        if cached_response:
            logger.info("Package list fetched from cache")
            return JsonResponse(json.loads(cached_response), safe=False)

        articles = request.session.get('articles', [])

        if not articles:
            self.queryset = self.queryset.none()
        else:
            # Получение всех посылок, которые были созданы пользователем
            self.queryset = self.queryset.filter(article__in=articles)

        response = super().list(request, *args, **kwargs)
        logger.info("Package list fetched successfully")

        cache.set(cache_key, json.dumps(response.data, cls=DjangoJSONEncoder), timeout=60*5)

        return response

    def retrieve(self, request, *args, **kwargs):
        """Получение информации о посылке по её ID.
        Пользователь может просматривать только свои посылки"""

        # TODO вынести кеш в отдельный метод
        package_id = kwargs.get('pk', None)
        session_key = request.session.session_key
        cache_key = f"package_{package_id}_{session_key}"
        cached_response = cache.get(cache_key)

        # Если ответ на запрос уже кеширован, то возвращаем его
        if cached_response:
            logger.info(f"Package with article {cached_response['article']} fetched from cache")
            return JsonResponse(cached_response, safe=False)

        response = super().retrieve(request, *args, **kwargs)

        # Если посылка не принадлежит пользователю, то пользователь не имеет права на её просмотр
        if response.data['article'] not in request.session.get('articles', []):
            logger.debug(f"Permission denied for accessing package with article {response.data['article']}")
            raise PermissionDenied

        logger.info(f"Package with article {response.data['article']} successfully retrieved")
        cache.set(cache_key, response.data, timeout=60 * 5)

        return response

    def get_serializer_class(self):
        if self.action == 'create':
            return PackageCreateSerializer
        return super().get_serializer_class()


@extend_schema(tags=['Types'])
@method_decorator(cache_page(60*5), name='dispatch')
class TypeListAPIView(ListAPIView):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer
