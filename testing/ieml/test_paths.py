from unittest.case import TestCase

from ieml.paths.paths import Path, MultiplicativePath, Coordinate
from ieml.paths.tools import path


class TestPaths(TestCase):
    def test_path_parser(self):
        p = path("t:sa:sa0:f")
        self.assertIsInstance(p, MultiplicativePath)
        self.assertTrue(all(isinstance(c, Coordinate) for c in p.children))