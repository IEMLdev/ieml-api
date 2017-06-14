import unittest

from ieml.ieml_objects.tools import RandomPoolIEMLObjectGenerator, ieml
from ieml.usl.template import Template


class TestTemplate(unittest.TestCase):
    def setUp(self):
        self.generator = RandomPoolIEMLObjectGenerator()

    def test_build_template(self):
        w = ieml("[([E:M:T:.]+[f.e.-s.i.-']+[g.-'U:M:.-'n.o.-s.o.-',])*([x.a.-]+[M:U:.p.-])]")
        t = Template(w, ['r0', 'r2', 'f1'])
        t.build()
        self.assertEqual(len(set(t)), 3*3*3)
