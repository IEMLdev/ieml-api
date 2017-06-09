from django_mongoengine import Document, fields

from .tag import USLField


class Document(Document):
    title = fields.StringField(required=True,)
    source = fields.StringField(required=True,)
    authors = fields.ListField(fields.StringField(), blank=True, default=list,)
    created_on = fields.DateTimeField(blank=True, null=True,)
    url = fields.URLField(verify_exists=True, required=True,)
    usl = USLField(blank=True, null=True, required=False,)
    description = fields.StringField(required=False, blank=True, null=True,)
    tags = fields.ListField(fields.StringField(), required=False, default=list, blank=True,)
    image = fields.URLField(verify_exists=True, null=True, required=False, blank=True,)
