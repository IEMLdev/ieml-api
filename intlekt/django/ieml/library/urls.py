from django.conf.urls import include, url
from rest_framework_mongoengine.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from . import views


router = DefaultRouter()
router.register(r'usls', views.USLViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
