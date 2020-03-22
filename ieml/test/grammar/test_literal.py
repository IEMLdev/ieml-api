import unittest

from ieml.usl.decoration.instance import InstancedUSL
from ieml.usl.decoration.parser.parser import PathParser
from ieml.usl.decoration.path import RolePath
from ieml.usl.usl import usl


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