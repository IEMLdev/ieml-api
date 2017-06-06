from mongoengine import connect

from collection import Collection
from document import Document
from tag import Tag

connect('ieml')

for c in Collection.objects:
    print(c)

d = Document()
d.title = 'doc'
d.source = 'twitter'
d.authors = ['lui']
d.url = 'http://docs.mongoengine.org/apireference.html#mongoengine.fields.EmbeddedDocumentListField'
d.description = 'desc'
d.save()

c = Collection()
c.title = 'abc'
c.authors = ['moi']
c.documents = [d]
c.save()
