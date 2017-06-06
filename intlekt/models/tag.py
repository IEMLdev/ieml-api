from intlekt import db


# TODO
# from functools import partial
# USLField = partial(db.ReferenceField, 'TODO')
USLField = db.ObjectIdField

class Tag(db.Document):
    usls = db.ListField(USLField())  # The meaning can depend on the context
    text = db.StringField(required=True, unique=True,)
