from django_mongoengine import EmbeddedDocument, fields


class CollectedSource(EmbeddedDocument):
    driver = fields.ReferenceField('SourceDriver', blank=False,)
    params = fields.DictField(blank=False,)
