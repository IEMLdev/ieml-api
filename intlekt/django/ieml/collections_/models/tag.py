from django_mongoengine import Document, fields

"""
from functools import partial
USLField = partial(fields.ReferenceField, 'USL')
"""
USLField = fields.StringField


class Tag(Document):
    """An IEML-translated word used to tag documents."""

    # The meaning can depend on the context, so a tag may have multiple usls.
    # Cannot be empty for the Mongo collection to contain translated tags only.
    # If it could be, there would be two ways to mark a tag as not translated:
    # not in the Mongo collection or with its `usls` attribute empty. It would
    # introduce additional parsing.
    usls = fields.ListField(USLField(),)
    text = fields.StringField(unique=True,)
