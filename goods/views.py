import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from goods.models import Package, Type
from goods.serializers import TypeSerializer, PackageRetrieveListSerializer, PackageCreateSerializer


logger = logging.getLogger(__name__)


class PackageViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Package.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type']

    def create(self, request, *args, **kwargs):
        """Метод создаёт посылку и сохраняет её уникальный артикул в сессию
        для того, чтобы пользователь мог просматривать свои посылки.
        (У пользователя нет возможности просматривать чужие посылки)"""

        response = super().create(request, *args, **kwargs)
        article = response.data['article']

        if 'articles' not in request.session:
            request.session['articles'] = []

        request.session['articles'].append(article)
        request.session.modified = True

        return response

    def list(self, request, *args, **kwargs):
        """Получение списка посылок, которые были созданы пользователем.
        Также возможна фильтрация по типу посылки и факту наличия
        рассчитанной стоимости доставки"""

        articles = request.session.get('articles', [])

        if not articles:
            self.queryset = self.queryset.none()
        else:
            # Получение всех посылок, которые были созданы пользователем
            self.queryset = self.queryset.filter(article__in=articles)

        # Если передан параметр filter, то происходит фильтрация по типу посылки или факту наличия стоимости доставки
        type_filter = request.query_params.get('filter')  # todo переименовать тогда эту переменную просто в filter, т.к фильтрация может быть не только по типу посылки
        if type_filter:
            self.queryset = self.queryset.filter(type_id=type_filter)

        response = super().list(request, *args, **kwargs)

        return response

    def retrieve(self, request, *args, **kwargs):
        """Получение информации о посылке по её ID.
        Пользователь может просматривать только свои посылки"""

        response = super().retrieve(request, *args, **kwargs)

        # Если посылка не принадлежит пользователю, то пользователь не имеет права на её просмотр
        if response.data['article'] not in request.session.get('articles', []):
            raise PermissionDenied

        return response

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return PackageRetrieveListSerializer
        elif self.action == 'create':
            return PackageCreateSerializer
        return super().get_serializer_class()


class TypeListAPIView(ListAPIView):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer
