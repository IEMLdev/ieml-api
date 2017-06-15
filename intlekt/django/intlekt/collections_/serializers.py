import pycountry

from rest_framework_mongoengine import serializers as mongoserializers
from rest_framework_mongoengine import fields as mongofields
from rest_framework import serializers

from . import models


def validate_set(list_):
    if len(set(list_)) != len(list_):
        raise serializers.ValidationError('Cannot have duplicates.')


def validate_posts_dict(posts):
    for key, post in posts.items():
        if key != str(post['document'].id):
            raise serializers.ValidationError(
                "The key '{0}' must be equal to the 'document' field value "
                "'{1}'.".format(key, post['document'].id)
            )


def validate_language(language):
    try:
        pycountry.languages.get(alpha_2=language)
    except KeyError:
        raise serializers.ValidationError('Bad format. See ISO 639-1.')


class PostSerializer(mongoserializers.EmbeddedDocumentSerializer):
    class Meta:
        model = models.Post
        fields = '__all__'
        extra_kwargs = {
            'collected_on': {
                'format': '%Y-%m-%d',
                'input_formats': ['%Y-%m-%d'],
            },
            'description': {'allow_blank': True},
            'tags': {'validators': [validate_set]},
        }


class CollectionSerializer(mongoserializers.DocumentSerializer):
    posts = mongofields.DictField(
        child=PostSerializer(),
        required=False,
        validators=[validate_posts_dict],
    )

    class Meta:
        model = models.Collection
        fields = '__all__'
        read_only_fields = ('created_on', 'updated_on',)
        extra_kwargs = {
            'created_on': {'format': '%Y-%m-%d'},
            'updated_on': {'format': '%Y-%m-%d'},
            'authors': {'validators': [validate_set]},
        }


class DocumentSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.Document
        fields = '__all__'
        extra_kwargs = {
            'created_on': {
                'format': '%Y-%m-%d',
                'input_formats': ['%Y-%m-%d'],
            },
            'authors': {'validators': [validate_set]},
            'keywords': {'validators': [validate_set]},
            'language': {'validators': [validate_language]},
            'title': {'allow_blank': True},
        }


class TagSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.Tag
        fields = '__all__'
        extra_kwargs = {
            'usls': {'validators': [validate_set]},
        }


class SourceSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.Source
        fields = '__all__'


class SourceDriverSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.SourceDriver
        fields = '__all__'
