import datetime as dt

from intlekt import db

from .document import Document


class Collection(db.Document):
    title = db.StringField(required=True, unique=True,)
    authors = db.ListField(required=True, field=db.StringField(),)
    created_on = db.DateTimeField(required=True, default=dt.datetime.now,)
    updated_on = db.DateTimeField(required=True, default=dt.datetime.now,)
    documents = db.ListField(db.ReferenceField(Document))
