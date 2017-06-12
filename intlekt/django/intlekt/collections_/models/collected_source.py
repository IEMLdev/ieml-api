from django_mongoengine import EmbeddedDocument, fields


class CollectedSource(EmbeddedDocument):
    driver = fields.ReferenceField('SourceDriver', required=True,)
    params = fields.DictField(required=True,)
