from flask_mongorest.views import ResourceView
from flask_mongorest.resources import Resource
from flask_mongorest import methods

from intlekt import api

from ..models import Document


class DocumentResource(Resource):
    document = Document


@api.register(name='documents', url='/documents/')
class DocumentView(ResourceView):
    resource = DocumentResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List]
