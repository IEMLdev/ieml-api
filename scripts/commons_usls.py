from ieml.ieml_objects.sentences import Sentence, Clause
from ieml.ieml_objects.terms import term
from ieml.ieml_objects.words import Word, Morpheme
from ieml.usl.tools import usl

root = Word(Morpheme([term("i.i.-"),  # fabriquer
                     term("a.i.-")]),  # vendre
            Morpheme([term("E:S:.o.-"),  # vouloir futur
                      term("E:S:.wa.-"),  # 1ere personne pluriel
                      term("E:A:T:.")]))  # beaucoup


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
            Word(Morpheme([term("t.i.-s.i.-'u.T:.-U:.-'wo.-',B:.-',_M:.-',_;")])),  # véhicule a roue sans conducteur
            Word(Morpheme([term("E:E:T:.")]))  # COD
        ), Clause(
            root,
            Word(Morpheme([term("S:.-'B:.-'n.-S:.U:.-',")])),  # Europe
            Word(Morpheme([term("E:T:.f.-")]))  # dans
        )])),
        'translations': {
            'FR': "Nous avons l'intention de fabriquer et de vendre beaucoup de nos véhicules à roues sans conducteurs en Europe",
            'EN': "We intend to manufacture and sell a lot of our wheeled vehicles without drivers in Europe"
        },
        'keywords': {
            'FR': [],
            'EN': []
        }
    }
]

