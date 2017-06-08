from intlekt import db

from .tag import USLField


class Document(db.Document):
    title = db.StringField(required=True,)
    source = db.StringField(required=True,)
    authors = db.ListField(db.StringField(),)
    created_on = db.DateTimeField()
    url = db.URLField(verify_exists=True, required=True,)
    usl = USLField()
    description = db.StringField()
    tags = db.ListField(db.StringField(),)
    image = db.URLField(verify_exists=True,)
