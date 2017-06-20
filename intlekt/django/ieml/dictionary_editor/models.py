import datetime

from django_mongoengine import Document
from django_mongoengine.fields import StringField, FloatField, DateTimeField


class Feedback(Document):
    __doc__ = "A feedback on the distance calculation"
    term_src = StringField(required=True)
    term_dest = StringField(unique_with='term_src', required=True)
    relation = StringField(choices=('up', 'remove', 'down'), required=True)
    distance = FloatField()
    comment = StringField(default=str)
    date_modified = DateTimeField(default=datetime.datetime.now, required=True)

