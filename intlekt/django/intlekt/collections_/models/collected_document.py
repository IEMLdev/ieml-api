from django.utils import timezone
from django_mongoengine import EmbeddedDocument, fields

from .tag import USLField


class CollectedDocument(EmbeddedDocument):
    collected_on = fields.DateTimeField(default=timezone.now, blank=True,)
    usl = USLField(blank=True, null=True, required=False,)
    tags = fields.ListField(fields.StringField(), required=False, default=list, blank=True,)
    image = fields.URLField(verify_exists=True, null=True, required=False, blank=True,)
    url = fields.URLField(blank=True, null=True,)
    description = fields.StringField(required=False, blank=True, null=True,)
    hidden = fields.BooleanField(default=False, blank=True,)
