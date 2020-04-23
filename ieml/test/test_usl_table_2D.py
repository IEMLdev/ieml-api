import unittest
from itertools import chain

from ieml.usl import PolyMorpheme
from ieml.usl.decoration.path import path, PolymorphemePath
from ieml.usl.table import UslTable2D
from ieml.usl.usl import usl


class TestUslTable2D(unittest.TestCase):

	def test_table2d_lexeme(self):
		u = usl("[! E:A:.  ()(b.-S:.A:.-'S:.-'S:.-', m1(S: B: T:) m2(y. o. e. u. a. i.)) > E:A:. E:A:. (m1(E:U:T:. E:A:T:. E:S:T:. E:B:T:. E:T:T:.))(k.a.-k.a.-')]")

		root_group0 = path(">role>! E:A:.>content>group_0 1")
		root_group1 = path(">role>! E:A:.>content>group_1 2")
		actant_group0 = path(">role>E:A:. E:A:.>flexion")

		table = UslTable2D(u, rows=root_group0, columns=root_group1)
		self.assertEqual(table.rows, sorted(table.rows))
		self.assertEqual(table.columns, sorted(table.columns))

		cells = table.cells
		self.assertTrue(all(len(cells[0]) == len(row) for row in cells))
		dim = (len(cells), len(cells[0]))
		print(dim)
		self.assertEqual((root_group0.deference(u).cardinal, root_group1.deference(u).cardinal), dim)

		for c in chain.from_iterable(cells):
			self.assertEqual(c.cardinal, actant_group0.deference(u).cardinal)

	def test_table2d_word(self):
		u = usl("[! E:A:.  ()(b.-S:.A:.-'S:.-'S:.-', m1(S: B: T:) m2(y. o. e. u. a. i.)) > E:A:. E:A:. (m1(E:U:T:. E:A:T:. E:S:T:. E:B:T:. E:T:T:.))(k.a.-k.a.-')]")

		root_group0 = path(">role>! E:A:.>content")
		# root_group1 = path(">role>! E:A:.>content>group_1 2>")
		actant_group0 = path(">role>E:A:. E:A:.>flexion")

		table = UslTable2D(u, rows=root_group0, columns=actant_group0)
		self.assertEqual(table.rows, sorted(table.rows))
		self.assertEqual(table.columns, sorted(table.columns))

		cells = table.cells
		self.assertTrue(all(len(cells[0]) == len(row) for row in cells))
		dim = (len(cells), len(cells[0]))
		self.assertEqual((root_group0.deference(u).cardinal, actant_group0.deference(u).cardinal), dim)

	def check_table(self, u, root_group0, root_group1):
		table = UslTable2D(u, rows=root_group0, columns=root_group1)
		self.assertEqual(table.rows, sorted(table.rows))
		self.assertEqual(table.columns, sorted(table.columns))

		cells = table.cells
		self.assertTrue(all(len(cells[0]) == len(row) for row in cells))
		dim = (len(cells), len(cells[0]))
		print(dim)
		self.assertEqual((1 if root_group0 is None else root_group0.deference(u).cardinal,
						  root_group1.deference(u).cardinal), dim)

		for c in chain.from_iterable(cells):
			self.assertEqual(c.cardinal, 1)

		all_cells = set(chain.from_iterable(cells))

		self.assertEqual(len(all_cells), dim[0] * dim[1])

		self.assertEqual({PolyMorpheme([m]) for v in table.row_paths_variation for p, m in v},
						 set() if root_group0 is None else root_group0.deference(u).singular_sequences_set)

		self.assertEqual({PolyMorpheme([m]) for v in table.column_paths_variation for p, m in v},
						 root_group1.deference(u).singular_sequences_set)

		for r, cells_row in zip(table.rows, cells):
			for r_c, cell in zip(r.singular_sequences, cells_row):
				for m_r in r_c.morphemes:
					if not m_r.empty:
						self.assertIn(m_r, cell.morphemes)

		for c, cells_column in zip(table.columns, zip(*cells)):
			for c_r, cell in zip(c.singular_sequences, cells_column):
				for m_c in c_r.morphemes:
					if not m_c.empty:
						self.assertIn(m_c, cell.morphemes)

	def test_table2d_pm(self):
		pm_2d = [[usl("t.o.- m1(S:.E:A:S:.- S:.E:A:B:.- S:.E:A:T:.-)"), None, path(">group_0 1")],
				 [usl("n.-T:.A:.-' m1(u.l.- a.B:.- f.-S:.U:.-' f.-T:.A:.-') m1(d.-h.-')"), path(">group_0 1"), path(">group_1 1")]]

		for u, group0, group1 in pm_2d:
			self.check_table(u, group0, group1)

	def test_table3d_pm(self):
		u = usl("l.-T:.U:.-',n.-T:.A:.-',b.-S:.A:.-'U:.-'U:.-',_ m1(E:S:.x.- S:.E:A:S:.- T:.E:A:T:.-) m1(u.A:.- a.S:.- t.o.-c.-' k.i.-t.i.-t.u.-' n.-T:.A:.-' l.-T:.U:.-',n.-T:.A:.-',m.-B:.U:.-'m.-B:.U:.-'E:A:T:.-',_ l.-T:.U:.-',n.-T:.A:.-',d.-S:.U:.-',_) m1(p.E:A:S:.- E:.-U:.d.-l.-')")
		root_group0 = path(">group_0 1")
		# root_group1 = path(">group_1 1")

		table = UslTable2D(u, rows=None, columns=root_group0)
		self.assertEqual(table.rows, sorted(table.rows))
		self.assertEqual(table.columns, sorted(table.columns))

		cells = table.cells
		self.assertTrue(all(len(cells[0]) == len(row) for row in cells))
		dim = (len(cells), len(cells[0]))
		print(dim)
		dim_column = root_group0.deference(u).cardinal

		self.assertEqual((u.cardinal//dim_column, dim_column), dim)

		for c in chain.from_iterable(cells):
			self.assertEqual(c.cardinal, 1)

		all_cells = set(chain.from_iterable(cells))

		self.assertEqual(len(all_cells), dim[0] * dim[1])
		self.assertEqual({PolyMorpheme([m]) for v in table.column_paths_variation for p, m in v}, root_group0.deference(u).singular_sequences_set)

		# self.assertEqual(set(table.columns), root_group0.deference(u).singular_sequences_set)

		for r, cells_row in zip(table.rows, cells):
			for r_c, cell in zip(r.singular_sequences, cells_row):

				for m_r in r_c.morphemes:
					if not m_r.empty:
						self.assertIn(m_r, cell.morphemes)

		for c, cells_column in zip(table.columns, zip(*cells)):
			for c_r, cell in zip(c.singular_sequences, cells_column):

				for m_c in c_r.morphemes:
					if not m_c.empty:
						self.assertIn(m_c, cell.morphemes)

	def test_table_2d_paradigm_pm(self):
		u = usl("l.-T:.U:.-',n.-T:.A:.-',b.-S:.A:.-'U:.-'U:.-',_ m1(E:S:.x.- S:.E:A:S:.- T:.E:A:T:.-) m1(u.A:.- a.S:.- t.o.-c.-' k.i.-t.i.-t.u.-' n.-T:.A:.-' l.-T:.U:.-',n.-T:.A:.-',m.-B:.U:.-'m.-B:.U:.-'E:A:T:.-',_ l.-T:.U:.-',n.-T:.A:.-',d.-S:.U:.-',_) m1(p.E:A:S:.- E:.-U:.d.-l.-')")
		root_group0 = path(">group_0 1")
		root_group1 = path(">group_1 1")

		table = UslTable2D(u, rows=root_group1, columns=root_group0)
		self.assertEqual(table.rows, sorted(table.rows))
		self.assertEqual(table.columns, sorted(table.columns))

		cells = table.cells
		self.assertTrue(all(len(cells[0]) == len(row) for row in cells))
		dim = (len(cells), len(cells[0]))
		print(dim)
		dim_column = root_group0.deference(u).cardinal
		dim_row = root_group1.deference(u).cardinal

		self.assertEqual((dim_row, dim_column), dim)
		self.assertEqual(dim[0] * dim[1] * 3, u.cardinal)

		all_cells = list(chain.from_iterable(cells))

		for c in all_cells:
			self.assertEqual(c.cardinal, 3)

		self.assertEqual(len(all_cells), dim[0] * dim[1])
		self.assertEqual(len(all_cells), len(set(all_cells)))

		self.assertEqual({PolyMorpheme([m]) for v in table.column_paths_variation for p, m in v},
						root_group0.deference(u).singular_sequences_set)

		self.assertEqual({PolyMorpheme([m]) for v in table.row_paths_variation for p, m in v},
						root_group1.deference(u).singular_sequences_set)

		for r, cells_row in zip(table.rows, cells):
			for r_c, cell in zip(r.singular_sequences, cells_row):

				for m_r in r_c.morphemes:
					if not m_r.empty:
						self.assertIn(m_r, cell.morphemes)

		for c, cells_column in zip(table.columns, zip(*cells)):
			for c_r, cell in zip(c.singular_sequences, cells_column):

				for m_c in c_r.morphemes:
					if not m_c.empty:
						self.assertIn(m_c, cell.morphemes)

	def test_table_lexeme_flexion_content_paradigm(self):
		u = usl("(m1(E:.wo.U:.-t.o.-' E:.wo.A:.-t.o.-'))(n.-T:.A:.-' m1(E:T:S:. E:T:T:. we.f.T:.- u.A:.- p.E:A:S:.- s.-S:.A:.-') m1(E:S:.x.- n.-T:.U:.-'))")
		root_group0 = path(">flexion")
		root_group1 = path(">content")

		table = UslTable2D(u, rows=root_group1, columns=root_group0)
		self.assertEqual(table.rows, sorted(table.rows))

		self.assertEqual(table.columns, sorted(table.columns))

		cells = table.cells
		self.assertTrue(all(len(cells[0]) == len(row) for row in cells))
		dim = (len(cells), len(cells[0]))
		print(dim)
		dim_column = root_group0.deference(u).cardinal
		dim_row = root_group1.deference(u).cardinal

		self.assertEqual((dim_row, dim_column), dim)
		self.assertEqual(dim[0] * dim[1], u.cardinal)

		all_cells = list(chain.from_iterable(cells))

		for c in all_cells:
			self.assertEqual(c.cardinal, 1)

		self.assertEqual(len(all_cells), dim[0] * dim[1])
		self.assertEqual(len(all_cells), len(set(all_cells)))

		self.assertEqual({PolyMorpheme([m]) for v in table.column_paths_variation for p, m in v},
						root_group0.deference(u).singular_sequences_set)

		# self.assertEqual({m for v in table.row_paths_variation for p, m in v if not m.empty},
		# 				set(root_group1.deference(u).morphemes))

		for r, cells_row in zip(table.rows, cells):
			self.assertEqual(r.cardinal, dim[1])

			for r_c, cell in zip(r.singular_sequences, cells_row):

				for m_r in r_c.morphemes:
					if not m_r.empty:
						self.assertIn(m_r, cell.morphemes)

		for c, cells_column in zip(table.columns, zip(*cells)):
			self.assertEqual(c.cardinal, dim[0])

			for c_r, cell in zip(c.singular_sequences, cells_column):

				for m_c in c_r.morphemes:
					if not m_c.empty:
						self.assertIn(m_c, cell.morphemes)

	def test_table_lexeme_content_flexion_paradigm(self):
		u = usl("(m1(E:.wo.U:.-t.o.-' E:.wo.A:.-t.o.-'))(n.-T:.A:.-' m1(E:T:S:. E:T:T:. we.f.T:.- u.A:.- p.E:A:S:.- s.-S:.A:.-') m1(E:S:.x.- n.-T:.U:.-'))")
		root_group1 = path(">flexion")
		root_group0 = path(">content")

		table = UslTable2D(u, rows=root_group1, columns=root_group0)
		self.assertEqual(table.rows, sorted(table.rows))

		self.assertEqual(table.columns, sorted(table.columns))

		cells = table.cells
		self.assertTrue(all(len(cells[0]) == len(row) for row in cells))
		dim = (len(cells), len(cells[0]))
		print(dim)
		dim_column = root_group0.deference(u).cardinal
		dim_row = root_group1.deference(u).cardinal

		self.assertEqual((dim_row, dim_column), dim)
		self.assertEqual(dim[0] * dim[1], u.cardinal)

		all_cells = list(chain.from_iterable(cells))

		for c in all_cells:
			self.assertEqual(c.cardinal, 1)

		self.assertEqual(len(all_cells), dim[0] * dim[1])
		self.assertEqual(len(all_cells), len(set(all_cells)))

		self.assertEqual({PolyMorpheme([m]) for v in table.row_paths_variation for p, m in v},
						root_group1.deference(u).singular_sequences_set)

		self.assertEqual({m for v in table.column_paths_variation for p, m in v if not m.empty},
						set(root_group0.deference(u).morphemes))

		for r, cells_row in zip(table.rows, cells):
			self.assertEqual(r.cardinal, dim[1])

			for r_c, cell in zip(r.singular_sequences, cells_row):

				for m_r in r_c.morphemes:
					if not m_r.empty:
						self.assertIn(m_r, cell.morphemes)

		for c, cells_column in zip(table.columns, zip(*cells)):
			self.assertEqual(c.cardinal, dim[0])

			for c_r, cell in zip(c.singular_sequences, cells_column):

				for m_c in c_r.morphemes:
					if not m_c.empty:
						self.assertIn(m_c, cell.morphemes)



if __name__ == '__main__':
	unittest.main()
