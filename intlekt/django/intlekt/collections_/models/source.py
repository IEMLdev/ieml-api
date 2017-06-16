from django_mongoengine import Document, fields


class Source(Document):
    """A source from which posts can be pulled. For instance, Twitter.
    
    Use a model instead of a simple `StringField` to avoid duplicates like
    "Twitter", "twitter", "touiteur".
    """

    name = fields.StringField(unique=True,)
