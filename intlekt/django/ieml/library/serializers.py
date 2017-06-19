import pycountry

from rest_framework_mongoengine import serializers as mongoserializers
from rest_framework_mongoengine import fields as mongofields
from rest_framework import serializers

from . import models


def validate_translations_dict(translations):
    for key in translations:
        try:
            pycountry.languages.get(alpha_2=key)
        except KeyError:
            raise serializers.ValidationError('Bad format. See ISO 639-1.')


class USLSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.USL
        fields = '__all__'
        extra_kwargs = {
            'translations': {'validators': [validate_translations_dict]},
        }

