from django_mongoengine import Document as Document_, fields


class Document(Document_):
    title = fields.StringField(required=True,)
    authors = fields.ListField(fields.StringField(), blank=True, default=list,)
    created_on = fields.DateTimeField(blank=True, null=True,)
    url = fields.URLField(required=True,)
