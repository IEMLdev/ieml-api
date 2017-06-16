from django.utils import timezone
from django_mongoengine import Document, fields
from mongoengine import signals


class Collection(Document):
    """A coherent group of documents gathered by a user."""

    title = fields.StringField(unique=True,)
    authors = fields.ListField(fields.StringField(),)
    created_on = fields.DateTimeField(default=timezone.now, blank=True,)
    updated_on = fields.DateTimeField(default=timezone.now, blank=True,)
    # Use a MapField instead of a ListField to ensure that a document is not
    # collected more than once
    posts = fields.MapField(
        fields.EmbeddedDocumentField('Post'),
        blank=True,
        help_text="The key must be equal to the 'document' field of the post.",
    )
    sources = fields.EmbeddedDocumentListField('CollectedSource', blank=True,)

    def __str__(self):
        return self.title

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.updated_on = timezone.now()


signals.pre_save.connect(Collection.pre_save, sender=Collection)
