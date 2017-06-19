from django_mongoengine import Document, fields


class SourceDriver(Document):
    """A service to pull posts from a source."""

    source = fields.ReferenceField('Source',)
    url = fields.URLField(unique=True,)
