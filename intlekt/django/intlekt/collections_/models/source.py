from django_mongoengine import Document, fields


class Source(Document):
    name = fields.StringField(unique=True,)
