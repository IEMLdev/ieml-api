from rest_framework_mongoengine import serializers as mongoserializers

from . import models


class FeedbackSerializer(mongoserializers.DocumentSerializer):
    class Meta:
        model = models.Feedback
        fields = '__all__'
        extra_kwargs = {'comment': {'allow_blank': True}}
