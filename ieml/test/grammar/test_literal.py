import unittest

from ieml.usl import PolyMorpheme
from ieml.usl.decoration.instance import InstancedUSL
from ieml.usl.decoration.parser.parser import PathParser
from ieml.usl.decoration.path import RolePath, PolymorphemePath, LexemePath, FlexionPath
from ieml.usl.parser import IEMLParser
from ieml.usl.usl import usl


VALIDS_PATHS = [
    "T: l.-T:.U:.-',n.-T:.A:.-',t.o.-f.o.-',_ m1(S:.E:A:T:.- T:.E:A:S:.-) m1(p.E:S:B:.- s.-S:.U:.-') [:group_0:s.-S:.U:.-' \"\"]"
]

class LiteralTestCase(unittest.TestCase):
    def test_parse(self):
        s = """[! E:A:.  ()(b.-S:.A:.-'S:.-'S:.-',) > E:A:. E:A:. ()(k.a.-k.a.-')] [:E:A:. E:A:.:content:constant:k.a.-k.a.-' "test"]"""
        res=usl(s)
        self.assertIsInstance(res, InstancedUSL)
        self.assertEqual(s, str(res))


    def test_parse_path(self):
        pathparser = PathParser()

        res = pathparser.parse(":E:A:. E:A:.")
        self.assertIsInstance(res, RolePath)

        res = pathparser.parse(":E:A:. E:A:.:content")
        self.assertIsInstance(res, RolePath)

        res = pathparser.parse(":E:A:. E:A:.:content:constant:k.a.-k.a.-'")
        self.assertIsInstance(res, RolePath)


        res = pathparser.parse(":flexion:k.a.-k.a.-'")
        self.assertIsInstance(res, LexemePath)
        self.assertIsInstance(res.child, FlexionPath)
        res = pathparser.parse(":flexion:E:S:.-U:.-t.o.-'")
        self.assertIsInstance(res, LexemePath)
        self.assertIsInstance(res.child, FlexionPath)




    def test_parse_empty_path(self):
        p = "T: l.-T:.U:.-',n.-T:.A:.-',t.o.-f.o.-',_ m1(S:.E:A:T:.- T:.E:A:S:.-) m1(p.E:S:B:.- s.-S:.U:.-') [:group_1:s.-S:.U:.-' \"\"]"
        pathparser = IEMLParser()
        res = pathparser.parse(p)
        self.assertIsInstance(res, InstancedUSL)
        self.assertIsInstance(res.usl, PolyMorpheme)
        self.assertTrue(len(res.decorations), 1)
        self.assertEqual(res.decorations[0].value, '')

        path = PathParser().parse(":group_1:s.-S:.U:.-'")
        self.assertIsInstance(path, PolymorphemePath)
        self.assertEqual(res.decorations[0].path, path)
