from django_mongoengine import Document, fields

"""
from functools import partial
USLField = partial(fields.ReferenceField, 'USL')
"""
USLField = fields.StringField


class Tag(Document):
    # The meaning can depend on the context so a tag may have multiple usls
    usls = fields.ListField(USLField(),)
    text = fields.StringField(required=True, unique=True,)
