import mongoengine as mg

from tag import USLField


class Document(mg.Document):
    title = mg.StringField(required=True,)
    source = mg.StringField(required=True,)
    authors = mg.ListField(field=mg.StringField(),)
    created_on = mg.DateTimeField()
    url = mg.URLField(verify_exists=True, required=True,)
    usl = USLField()
    description = mg.StringField()
    tags = mg.ListField(mg.StringField(),)
    image = mg.ImageField()
