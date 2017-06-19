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


class PostDoesNotExist(LookupError): pass


class PostViewSet(viewsets.ViewSet):
    def get_serializer(self, *args, **kwargs):
        return serializers.PostSerializer(*args, **kwargs)

    @classmethod
    def get_view_description(cls, html=False):
        return get_modelview_description(models.Post, html=html)

    @classmethod
    def get_post(cls, collection_id, post_id):
        try:
            collection = models.Collection.objects.get(id=collection_id)
        except models.Collection.DoesNotExist:
            raise PostDoesNotExist()

        posts = collection.posts
        try:
            return posts[post_id], collection
        except KeyError:
            raise PostDoesNotExist()

    def list(self, request, collection_id=None):
        if collection_id is None:
            return Response('Please specify a collection id.',
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            collection = models.Collection.objects.get(id=collection_id)
        except models.Collection.DoesNotExist:
            return Response('No such collection {}'.format(collection_id),
                            status=status.HTTP_404_NOT_FOUND)
        posts = collection.posts

        for key in posts:
            posts[key] = serializers.PostSerializer(posts[key]).data

        return Response(posts)

    def create(self, request, collection_id=None):
        if collection_id is None:
            return Response('Please specify a collection id.',
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            collection = models.Collection.objects.get(id=collection_id)
        except models.Collection.DoesNotExist:
            return Response('No such collection {}'.format(collection_id),
                            status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.PostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        post = serializer.save()

        if str(post.document.id) in collection.posts:
            return Response(
                {'document': ('This document has already been collected. '
                              'Please, use PUT or PATCH.')},
                status=status.HTTP_400_BAD_REQUEST
            )

        collection.posts[str(post.document.id)] = post
        collection.save()

        return Response(serializer.data)

    def retrieve(self, request, pk=None, collection_id=None):
        try:
            post, _ = self.get_post(collection_id, pk)
        except PostDoesNotExist:
            return Response(
                'No such post {} in collection {}'.format(
                    pk,
                    collection_id
                ),
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(serializers.PostSerializer(post).data)

    def update(self, request, pk=None, collection_id=None):
        try:
            post, collection = self.get_post(collection_id, pk)
        except PostDoesNotExist:
            return Response(
                'No such post {} in collection {}'.format(
                    pk,
                    collection_id
                ),
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = serializers.PostSerializer(post, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        post = serializer.save()
        collection.posts[pk] = post
        collection.save()

        return Response(serializer.data)

    def partial_update(self, request, pk=None, collection_id=None):
        try:
            post, collection = self.get_post(collection_id, pk)
        except PostDoesNotExist:
            return Response(
                'No such post {} in collection {}'.format(
                    pk,
                    collection_id
                ),
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = serializers.PostSerializer(
            post,
            data=request.data,
            partial=True,
        )
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        post = serializer.save()
        collection.posts[pk] = post
        collection.save()

        return Response(serializer.data)

    def destroy(self, request, pk=None, collection_id=None):
        try:
            _, collection = self.get_post(collection_id, pk)
        except PostDoesNotExist:
            return Response(
                'No such post {} in collection {}'.format(
                    pk,
                    collection_id
                ),
                status=status.HTTP_404_NOT_FOUND
            )

        collection.posts.pop(pk, None)
        collection.save()

        return Response('')


class CollectionViewSet(mongoviewsets.ModelViewSet):
    queryset = models.Collection.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.CollectionSerializer

    @classmethod
    def get_view_description(cls, html=False):
        return get_modelview_description(models.Collection, html=html)

    def get_queryset(self):
        return models.Collection.objects.all()


class DocumentViewSet(mongoviewsets.ModelViewSet):
    queryset = models.Document.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.DocumentSerializer

    @classmethod
    def get_view_description(cls, html=False):
        return get_modelview_description(models.Document, html=html)

    def get_queryset(self):
        return models.Document.objects.all()


class TagViewSet(mongoviewsets.ModelViewSet):
    queryset = models.Tag.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.TagSerializer

    @classmethod
    def get_view_description(cls, html=False):
        return get_modelview_description(models.Tag, html=html)

    def get_queryset(self):
        return models.Tag.objects.all()


class SourceViewSet(mongoviewsets.ModelViewSet):
    queryset = models.Source.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.SourceSerializer

    @classmethod
    def get_view_description(cls, html=False):
        return get_modelview_description(models.Source, html=html)

    def get_queryset(self):
        return models.Source.objects.all()


class SourceDriverViewSet(mongoviewsets.ModelViewSet):
    queryset = models.SourceDriver.objects.all()
    lookup_field = 'id'
    serializer_class = serializers.SourceDriverSerializer

    @classmethod
    def get_view_description(cls, html=False):
        return get_modelview_description(models.SourceDriver, html=html)

    def get_queryset(self):
        return models.SourceDriver.objects.all()
