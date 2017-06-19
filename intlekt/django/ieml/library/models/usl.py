from django_mongoengine import Document, fields


class USL(Document):
    # The value of the field is the name of the corresponding Python class
    GRAMMATICAL_TYPES = (
        ('Word', 'word'),
        ('Sentence', 'sentence'),
        ('SuperSentence', 'super sentence'),
    )

    ieml_text = fields.StringField(unique=True,)
    grammatical_type = fields.StringField(choices=GRAMMATICAL_TYPES,)
    # Cannot be blank because users work with translations,
    # not IEML texts directly.
    translations = fields.MapField(
        fields.StringField(),
        help_text=('Translations in natural languages. '
                   'Use the ISO 639-1 format for the keys.'),
    )

    meta = {
        'ordering': ['ieml_text'],
        'indexes': [
            'ieml_text',
        ],
    }
