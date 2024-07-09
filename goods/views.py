from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from goods.models import Package, Type
from goods.serializers import TypeSerializer, PackageListSerializer, PackageCreateSerializer


class PackageViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Package.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type']

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        article = response.data['article']

        if 'articles' not in request.session:
            request.session['articles'] = []

        request.session['articles'].append(article)
        request.session.modified = True

        return response

    def list(self, request, *args, **kwargs):
        articles = request.session.get('articles', [])

        if not articles:
            self.queryset = self.queryset.none()
        else:
            self.queryset = self.queryset.filter(article__in=articles)

        type_filter = request.query_params.get('filter')
        if type_filter:
            self.queryset = self.queryset.filter(type_id=type_filter)

        response = super().list(request, *args, **kwargs)

        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        package = response.data

        if package['article'] not in request.session.get('articles', []):
            raise PermissionDenied

        return response

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return PackageListSerializer
        elif self.action == 'create':
            return PackageCreateSerializer
        return super().get_serializer_class()


class TypeListAPIView(ListAPIView):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer
