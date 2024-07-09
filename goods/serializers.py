import logging

from rest_framework import serializers

from goods.models import Package, Type


logger = logging.getLogger(__name__)


class PackageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'
        read_only_fields = ('article', 'delivery_cost')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        logger.debug(f"Serializing package: {representation}")
        return {'article': representation['article']}


class PackageRetrieveListSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(slug_field='name', queryset=Type.objects.all())

    class Meta:
        model = Package
        fields = ('id', 'name', 'weight', 'type', 'cost', 'delivery_cost', 'article')


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ('id', 'name')
