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



from rest_framework_mongoengine import viewsets as mongoviewsets
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import detail_route

from . import models
from . import serializers


class CollectedDocumentDoesNotExist(LookupError): pass


class CollectedDocumentViewSet(viewsets.ViewSet):
    @classmethod
    def get_document(cls, collection_id, document_id):
        try:
            collection = models.Collection.objects.get(id=collection_id)
        except models.Collection.DoesNotExist:
            raise CollectedDocumentDoesNotExist()

        documents = collection.documents
        try:
            return documents[document_id], collection
        except KeyError:
            raise CollectedDocumentDoesNotExist()

    def list(self, request, collection_id=None):
        if collection_id is None:
            return Response('Please specify a collection id.',
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            collection = models.Collection.objects.get(id=collection_id)
        except models.Collection.DoesNotExist:
            return Response('No such collection {}'.format(collection_id),
                            status=status.HTTP_404_NOT_FOUND)
        documents = collection.documents

        for key in documents:
            documents[key] = serializers.CollectedDocumentSerializer(documents[key]).data

        return Response(documents)

    def create(self, request, collection_id=None):
        if collection_id is None:
            return Response('Please specify a collection id.',
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            collection = models.Collection.objects.get(id=collection_id)
        except models.Collection.DoesNotExist:
            return Response('No such collection {}'.format(collection_id),
                            status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.CollectedDocumentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        collected_document = serializer.save()

        if str(collected_document.document.id) in collection.documents:
            return Response(
                {'document': ('This document has already been collected. '
                              'Please, use PUT or PATCH.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        collection.documents[str(collected_document.document.id)] = collected_document
        collection.save()

        return Response(serializer.data)

    def retrieve(self, request, pk=None, collection_id=None):
        try:
            document, _ = self.get_document(collection_id, pk)
        except CollectedDocumentDoesNotExist:
            return Response(
                'No such collected document {} in collection {}'.format(
                    pk,
                    collection_id
                ),
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(serializers.CollectedDocumentSerializer(document).data)

    def update(self, request, pk=None, collection_id=None):
        try:
            document, collection = self.get_document(collection_id, pk)
        except CollectedDocumentDoesNotExist:
            return Response(
                'No such collected document {} in collection {}'.format(
                    pk,
                    collection_id
                ),
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = serializers.CollectedDocumentSerializer(document, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        document = serializer.save()
        collection.documents[pk] = document
        collection.save()

        return Response(serializer.data)

    def partial_update(self, request, pk=None, collection_id=None):
        try:
            document, collection = self.get_document(collection_id, pk)
        except CollectedDocumentDoesNotExist:
            return Response(
                'No such collected document {} in collection {}'.format(
                    pk,
                    collection_id
                ),
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = serializers.CollectedDocumentSerializer(
            document,
            data=request.data,
            partial=True,
        )
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        document = serializer.save()
        collection.documents[pk] = document
        collection.save()

        return Response(serializer.data)

    def destroy(self, request, pk=None, collection_id=None):
        try:
            _, collection = self.get_document(collection_id, pk)
        except CollectedDocumentDoesNotExist:
            return Response(
                'No such collected document {} in collection {}'.format(
                    pk,
                    collection_id
                ),
                status=status.HTTP_404_NOT_FOUND
            )

        collection.documents.pop(pk, None)
        collection.save()

        return Response('')


class CollectionViewSet(mongoviewsets.ModelViewSet):
    """A group of documents related to the same topic."""

    queryset = models.Collection.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.CollectionSerializer

    def get_queryset(self):
        return models.Collection.objects.all()


class DocumentViewSet(mongoviewsets.ModelViewSet):
    """A document to be collected. Can be a tweet, an article, a pdf..."""

    queryset = models.Document.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.DocumentSerializer

    def get_queryset(self):
        return models.Document.objects.all()


class TagViewSet(mongoviewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.TagSerializer

    def get_queryset(self):
        return models.Tag.objects.all()


class SourceViewSet(mongoviewsets.ModelViewSet):
    queryset = models.Source.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.SourceSerializer

    def get_queryset(self):
        return models.Source.objects.all()


class SourceDriverViewSet(mongoviewsets.ModelViewSet):
    queryset = models.SourceDriver.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.SourceDriverSerializer

    def get_queryset(self):
        return models.SourceDriver.objects.all()
