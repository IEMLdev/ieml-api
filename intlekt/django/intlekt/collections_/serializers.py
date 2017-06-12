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


class TagSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.Tag
        fields = '__all__'


class SourceSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.Source
        fields = '__all__'


class SourceDriverSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.SourceDriver
        fields = '__all__'
