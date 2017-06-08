from rest_framework_mongoengine import serializers as mongoserializers

from . import models


class CollectionSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.Collection
        fields = '__all__'
        read_only_fields = ('created_on', 'updated_on',)


class DocumentSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.Document
        fields = '__all__'
        read_only_fields = ('created_on',)
