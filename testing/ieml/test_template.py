import unittest

from ieml.ieml_objects.tools import RandomPoolIEMLObjectGenerator, ieml
from ieml.usl.template import Template


class TestTemplate(unittest.TestCase):
    def test_build_template(self):
        w = ieml("[([E:M:T:.]+[f.e.-s.i.-']+[g.-'U:M:.-'n.o.-s.o.-',])*([x.a.-]+[M:U:.p.-])]")
        t = Template(w, ['r0', 'r2', 'f1'])
        self.assertEqual(len(set(t)), 3*3*3)

    def test_translation(self):
        w = ieml("[([M:M:.a.-]+[M:.-',M:.-',S:.-'B:.-'n.-S:.U:.-',_])*([E:U:T:.]+[E:U:.wa.-])]")
        t = Template(w, ['r0', 'r1'])
        translations = t.get_translations({'fr': 'Ces meilleurs "$0" de "$1"', 'en': 'These best "$0" of "$1"'}, {'r0': '$0', 'r1': '$1'})

        self.assertEqual(len(translations), len(list(t)))
        all_fr = set(t['fr'] for t in translations.values())
        self.assertIn('Ces meilleurs "scribe" de "Europe nord-centrale | Danemark, Suède, Norvège"', all_fr)
        self.assertIn('Ces meilleurs "interprète" de "Europe médiane est | Roumanie, Moldavie, Ukraine"', all_fr)

        w = ieml("[([M:M:.a.-]+[M:.-',M:.-',S:.-'B:.-'n.-S:.U:.-',_])*([E:U:T:.]+[E:U:.wa.-])]")
        t = Template(w, ['r0', 'r1'])
        translations_2 = t.get_translations({'fr': 'Ces meilleurs "r0" de "r1"', 'en': 'These best "r0" of "r1"'})
        self.assertDictEqual(translations, translations_2)

