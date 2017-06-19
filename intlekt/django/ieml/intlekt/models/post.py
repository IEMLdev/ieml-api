from django.utils import timezone
from django_mongoengine import EmbeddedDocument, fields

from .tag import USLField


class Post(EmbeddedDocument):
    """A collected document, i.e. a document with metadata to be used for
    indexing. For instance, a post can be a tweet refering to an article.
    """

    document = fields.ReferenceField('Document')
    collected_on = fields.DateTimeField()
    # Can be null because finding a correct usl is complex so the user may not
    # do it immediatly, and so do scrapers.
    usl = USLField(null=True, blank=True, default=None,)
    tags = fields.ListField(fields.StringField(), blank=True,)
    # For display purposes
    image = fields.URLField(verify_exists=True, null=True, default=None,)
    url = fields.URLField(null=True, default=None,)
    description = fields.StringField(blank=True, default="",)
    # To mark a document as irrelevant for the collection. Do not delete it to
    # keep track of its past presence.
    hidden = fields.BooleanField(default=False, blank=True,)
