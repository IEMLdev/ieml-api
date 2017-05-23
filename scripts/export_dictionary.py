import os
from ieml.ieml_objects.dictionary import Dictionary, save_dictionary
from ieml.script.operator import script
from ieml.script.tools import factorize
from models.terms.terms import TermsConnector as tc


def load_dictionary_from_db():

    dic = Dictionary(cache=False)

    for t in tc().root_paradigms():
        s = factorize(script(t['_id']))

        dic.add_term(s, root=True, inhibitions=t['INHIBITS'],
                     translation={
                        'fr': t['TAGS']['FR'],
                        'en': t['TAGS']['EN']
                     })

    for t in tc().get_all_terms():
        s = factorize(script(t['_id']))

        dic.add_term(s, translation={
                        'fr': t['TAGS']['FR'],
                        'en': t['TAGS']['EN']
                     })

    dic.compute_relations()
    dic.compute_ranks()

if __name__ == '__main__':
    print(os.getcwd())
    load_dictionary_from_db()
    save_dictionary("../data/dictionary")
