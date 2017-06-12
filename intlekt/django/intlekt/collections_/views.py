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
    """A document to be collected. Can be a tweet, an article, a pdf..."""

    queryset = models.Document.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.DocumentSerializer

    def get_queryset(self):
        return models.Document.objects.all()


class TagViewSet(viewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        return models.Tag.objects.all()


class SourceViewSet(viewsets.ModelViewSet):
    queryset = models.Source.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.SourceSerializer

    def get_queryset(self):
        return models.Source.objects.all()


class SourceDriverViewSet(viewsets.ModelViewSet):
    queryset = models.SourceDriver.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.SourceDriverSerializer

    def get_queryset(self):
        return models.SourceDriver.objects.all()
