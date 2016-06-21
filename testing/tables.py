from ieml.parsing.script import ScriptParser
from ieml.script.tables import generate_tables
import numpy as np
import unittest


class TableGenerationTest(unittest.TestCase):

    def setUp(self):
        self.parser = ScriptParser()

    def test_additive_script(self):
        script = self.parser.parse("O:B:.+M:S:A:+S:.")
        tables = generate_tables(script)
        row_headers_table1 = [self.parser.parse("O:B:.")]
        row_headers_table2 = [self.parser.parse("S:S:A:+S:."), self.parser.parse("B:S:A:+S:."), self.parser.parse("T:S:A:+S:.")]
        col_headers_table2 = [self.parser.parse("M:S:A:."), self.parser.parse("M:S:S:.")]

        table1_cells = np.empty(2, dtype="object")
        table1_cells[0] = self.parser.parse("U:B:.")
        table1_cells[1] = self.parser.parse("A:B:.")

        table2_cells = np.empty((3, 2), dtype="object")
        table2_cells[0][0] = self.parser.parse("S:S:A:.")
        table2_cells[0][1] = self.parser.parse("S:S:S:.")

        table2_cells[1][0] = self.parser.parse("B:S:A:.")
        table2_cells[1][1] = self.parser.parse("B:S:S:.")

        table2_cells[2][0] = self.parser.parse("T:S:A:.")
        table2_cells[2][1] = self.parser.parse("T:S:S:.")

        self.assertEqual(tables[0].headers[0], row_headers_table1)
        self.assertTrue((tables[0].cells == table1_cells).all())

        self.assertEqual(tables[1].headers[0], row_headers_table2)
        self.assertEqual(tables[1].headers[1], col_headers_table2)
        self.assertTrue((tables[1].cells == table2_cells).all())

    def test_3d_multiplicative_script(self):
        script = self.parser.parse("M:O:M:.")
        tables = generate_tables(script)
        row_headers = [self.parser.parse("S:O:M:."), self.parser.parse("B:O:M:."), self.parser.parse("T:O:M:.")]
        col_headers = [self.parser.parse("M:U:M:."), self.parser.parse("M:A:M:.")]
        tab_headers = [self.parser.parse("M:O:S:."), self.parser.parse("M:O:B:."), self.parser.parse("M:O:T:.")]
        # TODO: manually build the 3D table cells
        cells = np.empty((3, 2, 3), dtype="object")

    def test_2d_multiplicative_script(self):
        script = self.parser.parse("M:O:.")
        tables = generate_tables(script)
        row_headers = []
        col_headers = []
        cells = np.fromiter()

    def test_1d_multiplicative_script(self):
        script = self.parser.parse("O:+A:S:A:.")
        tables = generate_tables(script)
        row_headers = []
        cells = np.fromiter()
