import unittest

import numpy as np

from ieml.operator import sc
from ieml.script.parser import ScriptParser
from ieml.script.tables import generate_tables


class TableGenerationTest(unittest.TestCase):

    # TODO: Write tests that checks if the tabs are split correctly

    def setUp(self):
        self.parser = ScriptParser()

    def test_additive_script_layer_0(self):
        script = sc("I:")
        tables = generate_tables(script)
        row_headers = [self.parser.parse("I:"), ]
        col_headers = []
        tab_headers = []

        cells = np.empty(6, dtype=object)

        cells[0] = self.parser.parse("E:")
        cells[1] = self.parser.parse("U:")
        cells[2] = self.parser.parse("A:")
        cells[3] = self.parser.parse("S:")
        cells[4] = self.parser.parse("B:")
        cells[5] = self.parser.parse("T:")

        self.assertEqual(len(tables), 1, "Correct number of tables generated")
        self.assertTrue(tables[0].cells.shape == cells.shape, "Table has the correct shape")
        self.assertEqual(tables[0].headers[0], row_headers, "Row headers are generated correctly")
        self.assertEqual(tables[0].headers[1], col_headers, "Column headers are generated correctly")
        self.assertEqual(tables[0].headers[2], tab_headers, "Tab headers are generated correctly")
        self.assertTrue((tables[0].cells == cells).all(), "Cells are generated correctly")
        self.assertTrue(tables[0].paradigm == script, "Table has correct paradigm")

    def test_additive_script(self):
        script = self.parser.parse("O:B:.+M:S:A:+S:.")
        tables = generate_tables(script)

        paradigm1 = self.parser.parse("O:B:.")
        paradigm2 = self.parser.parse("M:S:A:+S:.")
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

        self.assertEqual(len(tables), 2, "Correct number of tables generated")
        self.assertTrue(tables[0].cells.shape == table1_cells.shape, "First table has the correct shape")
        self.assertTrue(tables[1].cells.shape == table2_cells.shape, "Second table has the correct shape")
        self.assertEqual(tables[0].headers[0], row_headers_table1, "Row headers are generated correctly")
        self.assertTrue(len(tables[0].headers[1]) == 0, "First table has no column headers")
        self.assertTrue(len(tables[0].headers[2]) == 0, "First table has no tab headers")
        self.assertTrue((tables[0].cells == table1_cells).all(), "Cells are generated correctly")
        self.assertEqual(tables[1].headers[0], row_headers_table2, "Row headers are generated correctly")
        self.assertEqual(tables[1].headers[1], col_headers_table2, "Column headers are generated correctly")
        self.assertTrue(len(tables[1].headers[2]) == 0, "Second table has no tab headers")
        self.assertTrue((tables[1].cells == table2_cells).all(), "Cells are generated correctly")
        self.assertTrue(tables[0].paradigm == paradigm1, "First table has correct paradigm")
        self.assertTrue(tables[1].paradigm == paradigm2, "Second table has correct paradigm")

    def test_3d_multiplicative_script(self):
        script = self.parser.parse("M:M:.-O:M:.-E:.-+s.y.-'")
        tables = generate_tables(script)

        row_headers = [self.parser.parse("s.-O:M:.-E:.-+s.y.-'"), self.parser.parse("b.-O:M:.-E:.-+s.y.-'"),
                       self.parser.parse("t.-O:M:.-E:.-+s.y.-'"), self.parser.parse("k.-O:M:.-E:.-+s.y.-'"),
                       self.parser.parse("m.-O:M:.-E:.-+s.y.-'"), self.parser.parse("n.-O:M:.-E:.-+s.y.-'"),
                       self.parser.parse("d.-O:M:.-E:.-+s.y.-'"), self.parser.parse("f.-O:M:.-E:.-+s.y.-'"),
                       self.parser.parse("l.-O:M:.-E:.-+s.y.-'")]

        col_headers = [self.parser.parse("M:M:.-y.-E:.-+s.y.-'"), self.parser.parse("M:M:.-o.-E:.-+s.y.-'"),
                       self.parser.parse("M:M:.-e.-E:.-+s.y.-'"), self.parser.parse("M:M:.-u.-E:.-+s.y.-'"),
                       self.parser.parse("M:M:.-a.-E:.-+s.y.-'"), self.parser.parse("M:M:.-i.-E:.-+s.y.-'")]

        tab_headers = [self.parser.parse("M:M:.-O:M:.-'"), self.parser.parse("M:M:.-O:M:.-s.y.-'")]

        cells = np.empty((9, 6, 2), dtype="object")

        cells[0][0][0] = self.parser.parse("s.-y.-'")
        cells[0][1][0] = self.parser.parse("s.-o.-'")
        cells[0][2][0] = self.parser.parse("s.-e.-'")
        cells[0][3][0] = self.parser.parse("s.-u.-'")
        cells[0][4][0] = self.parser.parse("s.-a.-'")
        cells[0][5][0] = self.parser.parse("s.-i.-'")
        cells[1][0][0] = self.parser.parse("b.-y.-'")
        cells[1][1][0] = self.parser.parse("b.-o.-'")
        cells[1][2][0] = self.parser.parse("b.-e.-'")
        cells[1][3][0] = self.parser.parse("b.-u.-'")
        cells[1][4][0] = self.parser.parse("b.-a.-'")
        cells[1][5][0] = self.parser.parse("b.-i.-'")
        cells[2][0][0] = self.parser.parse("t.-y.-'")
        cells[2][1][0] = self.parser.parse("t.-o.-'")
        cells[2][2][0] = self.parser.parse("t.-e.-'")
        cells[2][3][0] = self.parser.parse("t.-u.-'")
        cells[2][4][0] = self.parser.parse("t.-a.-'")
        cells[2][5][0] = self.parser.parse("t.-i.-'")
        cells[3][0][0] = self.parser.parse("k.-y.-'")
        cells[3][1][0] = self.parser.parse("k.-o.-'")
        cells[3][2][0] = self.parser.parse("k.-e.-'")
        cells[3][3][0] = self.parser.parse("k.-u.-'")
        cells[3][4][0] = self.parser.parse("k.-a.-'")
        cells[3][5][0] = self.parser.parse("k.-i.-'")
        cells[4][0][0] = self.parser.parse("m.-y.-'")
        cells[4][1][0] = self.parser.parse("m.-o.-'")
        cells[4][2][0] = self.parser.parse("m.-e.-'")
        cells[4][3][0] = self.parser.parse("m.-u.-'")
        cells[4][4][0] = self.parser.parse("m.-a.-'")
        cells[4][5][0] = self.parser.parse("m.-i.-'")
        cells[5][0][0] = self.parser.parse("n.-y.-'")
        cells[5][1][0] = self.parser.parse("n.-o.-'")
        cells[5][2][0] = self.parser.parse("n.-e.-'")
        cells[5][3][0] = self.parser.parse("n.-u.-'")
        cells[5][4][0] = self.parser.parse("n.-a.-'")
        cells[5][5][0] = self.parser.parse("n.-i.-'")
        cells[6][0][0] = self.parser.parse("d.-y.-'")
        cells[6][1][0] = self.parser.parse("d.-o.-'")
        cells[6][2][0] = self.parser.parse("d.-e.-'")
        cells[6][3][0] = self.parser.parse("d.-u.-'")
        cells[6][4][0] = self.parser.parse("d.-a.-'")
        cells[6][5][0] = self.parser.parse("d.-i.-'")
        cells[7][0][0] = self.parser.parse("f.-y.-'")
        cells[7][1][0] = self.parser.parse("f.-o.-'")
        cells[7][2][0] = self.parser.parse("f.-e.-'")
        cells[7][3][0] = self.parser.parse("f.-u.-'")
        cells[7][4][0] = self.parser.parse("f.-a.-'")
        cells[7][5][0] = self.parser.parse("f.-i.-'")
        cells[8][0][0] = self.parser.parse("l.-y.-'")
        cells[8][1][0] = self.parser.parse("l.-o.-'")
        cells[8][2][0] = self.parser.parse("l.-e.-'")
        cells[8][3][0] = self.parser.parse("l.-u.-'")
        cells[8][4][0] = self.parser.parse("l.-a.-'")
        cells[8][5][0] = self.parser.parse("l.-i.-'")

        cells[0][0][1] = self.parser.parse("s.-y.-s.y.-'")
        cells[0][1][1] = self.parser.parse("s.-o.-s.y.-'")
        cells[0][2][1] = self.parser.parse("s.-e.-s.y.-'")
        cells[0][3][1] = self.parser.parse("s.-u.-s.y.-'")
        cells[0][4][1] = self.parser.parse("s.-a.-s.y.-'")
        cells[0][5][1] = self.parser.parse("s.-i.-s.y.-'")
        cells[1][0][1] = self.parser.parse("b.-y.-s.y.-'")
        cells[1][1][1] = self.parser.parse("b.-o.-s.y.-'")
        cells[1][2][1] = self.parser.parse("b.-e.-s.y.-'")
        cells[1][3][1] = self.parser.parse("b.-u.-s.y.-'")
        cells[1][4][1] = self.parser.parse("b.-a.-s.y.-'")
        cells[1][5][1] = self.parser.parse("b.-i.-s.y.-'")
        cells[2][0][1] = self.parser.parse("t.-y.-s.y.-'")
        cells[2][1][1] = self.parser.parse("t.-o.-s.y.-'")
        cells[2][2][1] = self.parser.parse("t.-e.-s.y.-'")
        cells[2][3][1] = self.parser.parse("t.-u.-s.y.-'")
        cells[2][4][1] = self.parser.parse("t.-a.-s.y.-'")
        cells[2][5][1] = self.parser.parse("t.-i.-s.y.-'")
        cells[3][0][1] = self.parser.parse("k.-y.-s.y.-'")
        cells[3][1][1] = self.parser.parse("k.-o.-s.y.-'")
        cells[3][2][1] = self.parser.parse("k.-e.-s.y.-'")
        cells[3][3][1] = self.parser.parse("k.-u.-s.y.-'")
        cells[3][4][1] = self.parser.parse("k.-a.-s.y.-'")
        cells[3][5][1] = self.parser.parse("k.-i.-s.y.-'")
        cells[4][0][1] = self.parser.parse("m.-y.-s.y.-'")
        cells[4][1][1] = self.parser.parse("m.-o.-s.y.-'")
        cells[4][2][1] = self.parser.parse("m.-e.-s.y.-'")
        cells[4][3][1] = self.parser.parse("m.-u.-s.y.-'")
        cells[4][4][1] = self.parser.parse("m.-a.-s.y.-'")
        cells[4][5][1] = self.parser.parse("m.-i.-s.y.-'")
        cells[5][0][1] = self.parser.parse("n.-y.-s.y.-'")
        cells[5][1][1] = self.parser.parse("n.-o.-s.y.-'")
        cells[5][2][1] = self.parser.parse("n.-e.-s.y.-'")
        cells[5][3][1] = self.parser.parse("n.-u.-s.y.-'")
        cells[5][4][1] = self.parser.parse("n.-a.-s.y.-'")
        cells[5][5][1] = self.parser.parse("n.-i.-s.y.-'")
        cells[6][0][1] = self.parser.parse("d.-y.-s.y.-'")
        cells[6][1][1] = self.parser.parse("d.-o.-s.y.-'")
        cells[6][2][1] = self.parser.parse("d.-e.-s.y.-'")
        cells[6][3][1] = self.parser.parse("d.-u.-s.y.-'")
        cells[6][4][1] = self.parser.parse("d.-a.-s.y.-'")
        cells[6][5][1] = self.parser.parse("d.-i.-s.y.-'")
        cells[7][0][1] = self.parser.parse("f.-y.-s.y.-'")
        cells[7][1][1] = self.parser.parse("f.-o.-s.y.-'")
        cells[7][2][1] = self.parser.parse("f.-e.-s.y.-'")
        cells[7][3][1] = self.parser.parse("f.-u.-s.y.-'")
        cells[7][4][1] = self.parser.parse("f.-a.-s.y.-'")
        cells[7][5][1] = self.parser.parse("f.-i.-s.y.-'")
        cells[8][0][1] = self.parser.parse("l.-y.-s.y.-'")
        cells[8][1][1] = self.parser.parse("l.-o.-s.y.-'")
        cells[8][2][1] = self.parser.parse("l.-e.-s.y.-'")
        cells[8][3][1] = self.parser.parse("l.-u.-s.y.-'")
        cells[8][4][1] = self.parser.parse("l.-a.-s.y.-'")
        cells[8][5][1] = self.parser.parse("l.-i.-s.y.-'")

        self.assertEqual(len(tables), 1, "Correct number of tables generated")
        self.assertTrue(tables[0].cells.shape == cells.shape, "Table has the correct shape")
        self.assertEqual(tables[0].headers[0], row_headers, "Row headers are generated correctly")
        self.assertEqual(tables[0].headers[1], col_headers, "Column headers are generated correctly")
        self.assertEqual(tables[0].headers[2], tab_headers, "Tab headers are generated correctly")
        self.assertTrue((tables[0].cells == cells).all(), "Cells are generated correctly")
        self.assertTrue(tables[0].paradigm == script, "Table has correct paradigm")

    def test_2d_multiplicative_script(self):
        script = self.parser.parse("M:.E:A:M:.-")
        tables = generate_tables(script)
        row_headers = [self.parser.parse("S:.E:A:M:.-"), self.parser.parse("B:.E:A:M:.-"),
                       self.parser.parse("T:.E:A:M:.-")]
        col_headers = [self.parser.parse("M:.E:A:S:.-"), self.parser.parse("M:.E:A:B:.-"),
                       self.parser.parse("M:.E:A:T:.-")]
        tab_headers = []
        cells = np.empty((3, 3), dtype=object)

        cells[0][0] = self.parser.parse("S:.E:A:S:.-")
        cells[0][1] = self.parser.parse("S:.E:A:B:.-")
        cells[0][2] = self.parser.parse("S:.E:A:T:.-")
        cells[1][0] = self.parser.parse("B:.E:A:S:.-")
        cells[1][1] = self.parser.parse("B:.E:A:B:.-")
        cells[1][2] = self.parser.parse("B:.E:A:T:.-")
        cells[2][0] = self.parser.parse("T:.E:A:S:.-")
        cells[2][1] = self.parser.parse("T:.E:A:B:.-")
        cells[2][2] = self.parser.parse("T:.E:A:T:.-")

        self.assertEqual(len(tables), 1, "Correct number of tables generated")
        self.assertTrue(tables[0].cells.shape == cells.shape, "Table has the correct shape")
        self.assertEqual(tables[0].headers[0], row_headers, "Row headers are generated correctly")
        self.assertEqual(tables[0].headers[1], col_headers, "Column headers are generated correctly")
        self.assertEqual(tables[0].headers[2], tab_headers, "Tab headers are generated correctly")
        self.assertTrue((tables[0].cells == cells).all(), "Cells are generated correctly")
        self.assertTrue(tables[0].paradigm == script, "Table has correct paradigm")

    def test_1d_multiplicative_script(self):
        script = self.parser.parse("E:S:O:.")
        tables = generate_tables(script)
        row_headers = [self.parser.parse("E:S:O:.")]
        col_headers = []
        tab_headers = []

        cells = np.empty(2, dtype=object)

        cells[0] = self.parser.parse("E:S:U:.")
        cells[1] = self.parser.parse("E:S:A:.")

        self.assertEqual(len(tables), 1, "Correct number of tables generated")
        self.assertTrue(tables[0].cells.shape == cells.shape, "Table has the correct shape")
        self.assertEqual(tables[0].headers[0], row_headers, "Row headers are generated correctly")
        self.assertEqual(tables[0].headers[1], col_headers, "Column headers are generated correctly")
        self.assertEqual(tables[0].headers[2], tab_headers, "Tab headers are generated correctly")
        self.assertTrue((tables[0].cells == cells).all(), "Cells are generated correctly")
        self.assertTrue(tables[0].paradigm == script, "Table has correct paradigm")

    def test_row_of_paradigm(self):
        script = self.parser.parse("t.i.-s.i.-'u.S:.-U:.-'O:O:.-',")
        tables = generate_tables(script)
        cells = np.empty((2, 2), dtype=object)

        row_headers = [self.parser.parse("t.i.-s.i.-'u.S:.-U:.-'U:O:.-',"),
                       self.parser.parse("t.i.-s.i.-'u.S:.-U:.-'A:O:.-',")]
        col_headers = [self.parser.parse("t.i.-s.i.-'u.S:.-U:.-'O:U:.-',"),
                       self.parser.parse("t.i.-s.i.-'u.S:.-U:.-'O:A:.-',")]
        tab_headers = []

        cells[0][0] = self.parser.parse("t.i.-s.i.-'u.S:.-U:.-'wo.-',")
        cells[0][1] = self.parser.parse("t.i.-s.i.-'u.S:.-U:.-'wa.-',")
        cells[1][0] = self.parser.parse("t.i.-s.i.-'u.S:.-U:.-'wu.-',")
        cells[1][1] = self.parser.parse("t.i.-s.i.-'u.S:.-U:.-'we.-',")

        self.assertEqual(len(tables), 1, "Correct number of tables generated")
        self.assertTrue(tables[0].cells.shape == cells.shape, "Table has the correct shape")
        self.assertEqual(tables[0].headers[0], row_headers, "Row headers are generated correctly")
        self.assertEqual(tables[0].headers[1], col_headers, "Column headers are generated correctly")
        self.assertEqual(tables[0].headers[2], tab_headers, "Tab headers are generated correctly")
        self.assertTrue((tables[0].cells == cells).all(), "Cells are generated correctly")
        self.assertTrue(tables[0].paradigm == script, "Table has correct paradigm")
