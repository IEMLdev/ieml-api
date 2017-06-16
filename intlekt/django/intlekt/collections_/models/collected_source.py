from django_mongoengine import EmbeddedDocument, fields


class CollectedSource(EmbeddedDocument):
    """A request pattern for a source driver. For instance, all tweets having
    a particular tag. The posts to collect are described in the `params` field,
    the content of which depends on the driver API.
    """

    driver = fields.ReferenceField('SourceDriver', blank=False,)
    params = fields.DictField(
        # Cannot be blank because scrapers need to know which posts to collect
        # on the source
        blank=False,
        help_text='A dictionnary of parameters passed to the driver.',
    )
