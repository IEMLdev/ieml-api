from ieml.ieml_objects.sentences import Sentence, Clause
from ieml.ieml_objects.terms import Term
from ieml.ieml_objects.words import Word, Morpheme
from ieml.usl.tools import usl
from models.usls.usls import USLConnector

root = Word(Morpheme([Term("i.i.-"),  # fabriquer
                     Term("a.i.-")]),  # vendre
            Morpheme([Term("E:S:.o.-"),  # vouloir futur
                      Term("E:S:.wa.-"),  # 1ere personne pluriel
                      Term("E:A:T:.")]))  # beaucoup


objects = [
    {
        'usl': usl(root),
        'tags': {
            'FR': "Nous avons l'intention de fabriquer et de vendre beaucoup",
            'EN': "We intend to manufacture and sell a lot"
        },
        'keywords': {
            'FR': [],
            'EN': []
        }
    },
    {
        'usl': usl(Sentence([Clause(
            root,
            Word(Morpheme([Term("t.i.-s.i.-'u.T:.-U:.-'wo.-',B:.-',_M:.-',_;")])),  # véhicule a roue sans conducteur
            Word(Morpheme([Term("E:E:T:.")]))  # COD
        ), Clause(
            root,
            Word(Morpheme([Term("S:.-'B:.-'n.-S:.U:.-',")])),  # Europe
            Word(Morpheme([Term("E:T:.f.-")]))  # dans
        )])),
        'tags': {
            'FR': "Nous avons l'intention de fabriquer et de vendre beaucoup de nos véhicules à roues sans conducteurs en Europe",
            'EN': "We intend to manufacture and sell a lot of our wheeled vehicles without drivers in Europe"
        },
        'keywords': {
            'FR': [],
            'EN': []
        }
    }
]


def save_usls():
    usls = USLConnector()
    for o in objects:
        if usls.get(usl=o['usl']) is None:
            usls.save(**o)


def init_dev_db():
    save_usls()


if __name__ == '__main__':
    init_dev_db()
