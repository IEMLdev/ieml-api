from handlers.commons import exception_handler
from models.collections.sources import SourcesConnector
from pipeline.importer.scoopit import import_tags


@exception_handler
def collection_define_tag(body):
    SourcesConnector().set_ieml(body['url'], body['tag'], body['ieml'])
    return {'success': True}


@exception_handler
def collection_get_tags(body):
    url = body['url']

    s = SourcesConnector()
    if not s.get_source(url):
        import_tags(url)

    result = [{'tags': t['title'],
               'count': t['count'],
               'link': t['link'],
               'ieml': t['ieml']} for t in SourcesConnector().get_source(url)['tags']]

    return {'success': True,
            'tags': sorted(result, key=lambda d: d['count'], reverse=True)}

