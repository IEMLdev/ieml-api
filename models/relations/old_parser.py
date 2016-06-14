from urllib.parse import quote
from requests import post
from ieml.parsing.script import ScriptParser
from json import loads

def get_all_relations(script_ast):
    result = post('http://test-ieml.rhcloud.com/ScriptParser/rest/iemlparser/relationship2',
                  data={'iemltext': str(script_ast)})
    relations = loads(result.text)['relations']
    result = {}
    for rel in relations:
        result[rel['name']] = rel['stop']

    return result

if __name__ == '__main__':
    parser = ScriptParser()
    print(get_all_relations(parser.parse("M:.-O:.-'M:.-wa.e.-'t.x.-s.y.-',")))
