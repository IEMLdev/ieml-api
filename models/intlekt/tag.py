import mongoengine as mg


# TODO
# from functools import partial
# USLField = partial(mg.ReferenceField, 'TODO')
USLField = mg.ObjectIdField

class Tag(mg.Document):
    usls = mg.ListField(USLField())  # The meaning can depend on the context
    text = mg.StringField(required=True, unique=True, primary_key=True,)
