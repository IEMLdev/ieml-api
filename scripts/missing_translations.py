from ieml.parsing.parser import PropositionsParser
from models.intlekt.usl.usl_connector import UslConnector
from models.terms.terms import TermsConnector
from models.intlekt.constants import LANGUAGES
#faire les champs Spanish et portuguese même vide pour ne retourner qu'un seul objet python : JSON
connector = UslConnector()

usls_ieml = list(connector.usls.find())

to_translate = []

for el in usls_ieml:
    l_to_trans = set(LANGUAGES) - set(k['language'] for k in el['KEYWORDS'])
    keywords = el['KEYWORDS']
    keywords.extend([{
        'language': l,
        'DERIVED':'write here the %s translation'%l
    } for l in l_to_trans])

    to_translate.append({
        '_id': el['_id'],
        'KEYWORDS': keywords
    })

import pprint
import json
with open("missing_translations.txt", 'w') as fp:
    json.dump(to_translate, fp=fp, ensure_ascii=False, indent=True)
