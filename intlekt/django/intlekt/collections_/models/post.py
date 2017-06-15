from django.utils import timezone
from django_mongoengine import EmbeddedDocument, fields

from .tag import USLField


class Post(EmbeddedDocument):
    document = fields.ReferenceField('Document')
    collected_on = fields.DateTimeField()
    usl = USLField(null=True, blank=True, default=None,)
    tags = fields.ListField(fields.StringField(), blank=True,)
    image = fields.URLField(verify_exists=True, null=True, blank=True, default=None,)
    url = fields.URLField(blank=True, null=True, default=None,)
    description = fields.StringField(blank=True, default="",)
    hidden = fields.BooleanField(default=False, blank=True,)
