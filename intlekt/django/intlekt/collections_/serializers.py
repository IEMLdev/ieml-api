from rest_framework_mongoengine import serializers as mongoserializers
from rest_framework_mongoengine import fields as mongofields
from rest_framework import serializers

from . import models


class CollectedDocumentSerializer(mongoserializers.EmbeddedDocumentSerializer):
    class Meta:
        model = models.CollectedDocument
        fields = '__all__'
        extra_kwargs = {
            'collected_on': {
                'format': '%Y-%m-%d',
                'input_formats': ['%Y-%m-%d'],
            },
            'description': {'allow_blank': True},
        }


class CollectionSerializer(mongoserializers.DocumentSerializer):
    documents = mongofields.DictField(child=CollectedDocumentSerializer(), required=False,)

    class Meta:
        model = models.Collection
        fields = '__all__'
        read_only_fields = ('created_on', 'updated_on',)
        extra_kwargs = {
            'created_on': {'format': '%Y-%m-%d'},
            'updated_on': {'format': '%Y-%m-%d'},
        }


class CollectDocumentSerializer(serializers.Serializer):
    id = mongofields.ReferenceField(models.Document)
    document = CollectedDocumentSerializer()


class DocumentSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.Document
        fields = '__all__'
        extra_kwargs = {
            'created_on': {
                'format': '%Y-%m-%d',
                'input_formats': ['%Y-%m-%d'],
            },
        }


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
