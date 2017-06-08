from django_mongoengine import Document, fields

"""
from functools import partial
USLField = partial(fields.ReferenceField, 'USL')
"""
USLField = fields.StringField


class Tag(Document):
    usls = fields.ListField(USLField(), blank=True, default=list,)  # The meaning can depend on the context
    text = fields.StringField(required=True, unique=True,)
