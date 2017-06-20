from django.conf.urls import include, url
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register(r'feedback', FeedbackViewSet, base_name="feedback")
print(router.urls)

urlpatterns = [
    url(r'^', include(router.urls)),

    url(r'^feedback/(?P<term_src>[^/]*)$', FeedbackViewSet.as_view({'get': 'list'})),

    url(r'^version$', get_dictionary_version),
    url(r'^all$', all_ieml),

    url(r'^relations$', rels),
    url(r'^relations/visibility$', get_rel_visibility),

    url(r'^terms$', Terms.as_view()),
    url(r'^terms/ieml$', ieml_term_exists),
    url(r'^terms/FR', fr_tag_exists),
    url(r'^terms/EN', en_tag_exists),
    url(r'^terms/ranking$', get_ranking_from_term),

    url(r'^scripts/parse$', parse_ieml),
    url(r'^scripts/tables$', script_table),
    url(r'^login/', obtain_auth_token)
]
