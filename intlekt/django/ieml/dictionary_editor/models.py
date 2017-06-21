import datetime

from django_mongoengine import Document
from django_mongoengine.fields import StringField, FloatField, DateTimeField


class Feedback(Document):
    __doc__ = "A feedback on the distance calculation"
    term_src = StringField()
    term_dest = StringField(unique_with='term_src')
    relation = StringField(choices=('up', 'remove', 'down'))
    distance = FloatField(blank=True)
    comment = StringField(default=str, blank=True)
    date_modified = DateTimeField(default=datetime.datetime.now)

