from django.utils.encoding import smart_text
from rest_framework_mongoengine import viewsets as mongoviewsets
from rest_framework import viewsets
from rest_framework import status
from rest_framework.utils import formatting
from rest_framework.decorators import detail_route

from . import models
from . import serializers


def get_modelview_description(model, html=False):
    description = model.__doc__
    description = formatting.dedent(smart_text(description))
    if html:
        return formatting.markup_description(description)
    return description


class USLViewSet(mongoviewsets.ModelViewSet):
    queryset = models.USL.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.USLSerializer

    @classmethod
    def get_view_description(cls, html=False):
        return get_modelview_description(models.USL, html=html)

    def get_queryset(self):
        return models.USL.objects.all()
