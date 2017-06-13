from django.utils import timezone
from django_mongoengine import Document, fields
from mongoengine import signals


class Collection(Document):
    title = fields.StringField(unique=True,)
    authors = fields.ListField(fields.StringField(), required=False, blank=True, default=list,)
    created_on = fields.DateTimeField(default=timezone.now, blank=True,)
    updated_on = fields.DateTimeField(default=timezone.now, blank=True,)
    documents = fields.MapField(fields.EmbeddedDocumentField('CollectedDocument'), blank=True,)
    sources = fields.EmbeddedDocumentListField('CollectedSource', blank=True,)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.updated_on = timezone.now()


signals.pre_save.connect(Collection.pre_save, sender=Collection)
