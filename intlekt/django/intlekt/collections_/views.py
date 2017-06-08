# TODO: to be removed, for testing ui
from django.shortcuts import render

def home(request):
    return render(request, 'collections_/home.html')


from rest_framework_mongoengine import viewsets

from . import models
from . import serializers


class CollectionViewSet(viewsets.ModelViewSet):
    """A group of documents related to the same topic."""

    queryset = models.Collection.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.CollectionSerializer

    def get_queryset(self):
        return models.Collection.objects.all()


class DocumentViewSet(viewsets.ModelViewSet):
    """A document to be indexed. Can be a tweet, an article, a pdf..."""

    queryset = models.Document.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.DocumentSerializer

    def get_queryset(self):
        return models.Document.objects.all()
