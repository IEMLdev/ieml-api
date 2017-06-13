from django.conf.urls import include, url
from rest_framework_mongoengine.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r'collections', views.CollectionViewSet)
router.register(r'documents', views.DocumentViewSet)
router.register(r'sources', views.SourceViewSet)
router.register(r'source_drivers', views.SourceDriverViewSet)
router.register(r'tags', views.TagViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),

    # TODO: to be removed, for testing
    url(r'^ui/$', views.home),
    url(r'^scoopit/$', views.scoopit),
]
