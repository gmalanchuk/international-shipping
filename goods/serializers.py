from rest_framework import serializers

from goods.models import Package, Type


class PackageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'
        read_only_fields = ('article', 'created_at', 'updated_at')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return {'article': ret['article']}


class PackageListSerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(slug_field='name', queryset=Type.objects.all())

    class Meta:
        model = Package
        fields = '__all__'


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
