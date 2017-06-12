from django_mongoengine import Document, fields


class SourceDriver(Document):
    source = fields.ReferenceField('Source', required=True,)
    url = fields.URLField(unique=True, required=True,)
