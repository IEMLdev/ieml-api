from ieml.dictionary import term
from ieml.grammar import topic, fact, usl

root = topic([term("i.i.-"),  # fabriquer
             term("a.i.-")],  # vendre
            [term("E:S:.o.-"),  # vouloir futur
             term("E:S:.wa.-"),  # 1ere personne pluriel
             term("E:A:T:.")])  # beaucoup


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
        'usl': usl(fact([(
            root,
            topic([term("t.i.-s.i.-'u.T:.-U:.-'wo.-',B:.-',_M:.-',_;")]),  # véhicule a roue sans conducteur
            topic([term("E:E:T:.")])  # COD
        ), (
            root,
            topic([term("S:.-'B:.-'n.-S:.U:.-',")]),  # Europe
            topic([term("E:T:.f.-")])  # dans
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

