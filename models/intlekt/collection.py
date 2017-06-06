import datetime as dt

import mongoengine as mg


class Collection(mg.Document):
    title = mg.StringField(required=True, unique=True, primary_key=True,)
    authors = mg.ListField(required=True, field=mg.StringField(),)
    created_on = mg.DateTimeField(required=True, default=dt.datetime.now,)
    updated_on = mg.DateTimeField(required=True, default=dt.datetime.now,)
    documents = mg.EmbeddedDocumentListField('Document')
