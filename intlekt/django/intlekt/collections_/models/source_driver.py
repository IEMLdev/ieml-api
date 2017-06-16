from django_mongoengine import Document, fields


class SourceDriver(Document):
    source = fields.ReferenceField('Source',)
    url = fields.URLField(unique=True,)
