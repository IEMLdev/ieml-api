# TODO: to be removed, for testing ui
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from django.http import HttpResponse

def home(request):
    return render(request, 'collections_/home.html')

@require_http_methods(["POST"])
@csrf_exempt
def scoopit(request):
    print(request.body)

    return HttpResponse('scoopit')



from rest_framework_mongoengine import viewsets
from rest_framework import status
from rest_framework.decorators import detail_route

from . import models
from . import serializers


class CollectionViewSet(viewsets.ModelViewSet):
    """A group of documents related to the same topic."""

    queryset = models.Collection.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.CollectionSerializer

    def get_queryset(self):
        return models.Collection.objects.all()

    @detail_route(methods=['get', 'post', 'put'])
    def documents(self, request, *args, **kwargs):
        collection = self.get_object()
        if request.method == 'GET':
            return Response(
                serializers.CollectionSerializer(collection).data['documents']
            )

        serializer = serializers.CollectDocumentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        id_ = serializer.data['id']
        if request.method == 'POST' and id_ in collection.documents:
            return Response(
                {'id': ('This document has already been collected. '
                        'Use PUT instead.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'PUT' and id_ not in collection.documents:
            return Response(
                {'id': ('This document has not been collected yet. '
                        'Use POST instead.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        document = models.CollectedDocument(**serializer.data['document'])
        collection.documents[id_] = document
        collection.save()

        return Response(serializers.CollectedDocumentSerializer(document).data)


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
