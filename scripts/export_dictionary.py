import json
from ieml.ieml_objects.dictionary import Dictionary, save_dictionary, DICTIONARY_FOLDER
from ieml.script.operator import script
from ieml.script.tools import factorize


def load_dictionary_from_db():

    dic = Dictionary(cache=False)

    INHIBITIONS_MAP = {
        'FATHER_RELATION.SUBSTANCE': 'FATHER.SUBSTANCE',
        'FATHER_RELATION.ATTRIBUTE': 'FATHER.ATTRIBUTE',
        'FATHER_RELATION.MODE': 'FATHER.MODE',
        'TWIN_SIBLING': 'TWIN',
        'OPPOSED_SIBLING': 'OPPOSED',
        'ASSOCIATED_SIBLING': 'ASSOCIATED',
        'CROSSED_SIBLING': 'CROSSED'
    }

    for t in tc().root_paradigms():
        s = factorize(script(t['_id']))

        inhibitions = [INHIBITIONS_MAP[i] for i in t['INHIBITS']]
        dic.add_term(s, root=True, inhibitions=inhibitions,
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

    # dic.compute_relations()
    # dic.compute_ranks()
    # save_dictionary(DICTIONARY_FOLDER)

def add_terms_from_allieml(file):
    with open(file, 'r') as fp:
        allieml = json.load(fp)

    to_add = [t for t in allieml if t['_id'] not in Dictionary()]

    print("%d terms to be added"%len(to_add))

    for r in filter(lambda c: c['ROOT_PARADIGM'], to_add):
        print("Adding root : %s"%r['_id'])
        Dictionary().add_term(r['_id'], root=True, inhibitions=(),translation={'fr': r['FR'], 'en': r['EN']})

    for r in filter(lambda c: not c['ROOT_PARADIGM'], to_add):
        Dictionary().add_term(r['_id'], root=False, translation={'fr': r['FR'], 'en': r['EN']})

    Dictionary()._index = None

    Dictionary().compute_relations()
    Dictionary().compute_ranks()

    save_dictionary(DICTIONARY_FOLDER)


def convert_inhibitions():
    OLD_TO_NEW = {
        'FATHER.SUBSTANCE': 'father_substance',
        'FATHER.ATTRIBUTE': 'father_attribute',
        'FATHER.MODE': 'father_mode',

        'CHILDREN.SUBSTANCE': 'child_substance',
        'CHILDREN.ATTRIBUTE': 'child_attribute',
        'CHILDREN.MODE': 'child_mode',

        'OPPOSED': 'opposed',
        'CROSSED': "crossed",
        'ASSOCIATED': "associated",
        'TWIN': "twin"
    }

    Dictionary().inhibitions = {t: [OLD_TO_NEW[s] for s in Dictionary().inhibitions[t]] for t in Dictionary().inhibitions}
    save_dictionary(DICTIONARY_FOLDER)



if __name__ == '__main__':
    # load_dictionary_from_db()
    # # print(os.getcwd())
    # # load_dictionary_from_db()
    # # save_dictionary("../data/dictionary")
    # add_terms_from_allieml('../data/allieml.1')
    convert_inhibitions()