import unittest
from itertools import chain

from ieml.usl.decoration.path import path
from ieml.usl.table import UslTable2D
from ieml.usl.usl import usl


class TestUslTable2D(unittest.TestCase):

	def test_table2d_lexeme(self):
		u = usl("[! E:A:.  ()(b.-S:.A:.-'S:.-'S:.-', m1(S: B: T:) m2(y. o. e. u. a. i.)) > E:A:. E:A:. (m1(E:U:T:. E:A:T:. E:S:T:. E:B:T:. E:T:T:.))(k.a.-k.a.-')]")

		root_group0 = path(">role>! E:A:.>content>group_0 1")
		root_group1 = path(">role>! E:A:.>content>group_1 2")
		actant_group0 = path(">role>E:A:. E:A:.>flexion")

		table = UslTable2D(u, rows=root_group0, columns=root_group1)

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

		cells = table.cells
		self.assertTrue(all(len(cells[0]) == len(row) for row in cells))
		dim = (len(cells), len(cells[0]))
		self.assertEqual((root_group0.deference(u).cardinal, actant_group0.deference(u).cardinal), dim)

	def test_table2d_pm(self):
		u = usl("n.-T:.A:.-' m1(u.l.- a.B:.- f.-S:.U:.-' f.-T:.A:.-') m1(d.-h.-')")
		root_group0 = path(">group_0 1")
		root_group1 = path(">group_1 1")

		table = UslTable2D(u, rows=root_group0, columns=root_group1)

		cells = table.cells
		self.assertTrue(all(len(cells[0]) == len(row) for row in cells))
		dim = (len(cells), len(cells[0]))
		print(dim)
		self.assertEqual((root_group0.deference(u).cardinal, root_group1.deference(u).cardinal), dim)

		for c in chain.from_iterable(cells):
			self.assertEqual(c.cardinal, 1)

		all_cells = set(chain.from_iterable(cells))

		self.assertEqual(len(all_cells), dim[0] * dim[1])

		self.assertEqual(set(table.rows), root_group0.deference(u).singular_sequences_set)
		self.assertEqual(set(table.columns), root_group1.deference(u).singular_sequences_set)

		for r, cells_row in zip(table.rows, cells):
			for c, cell in zip(table.columns, cells_row):
				for m_r in r.morphemes:
					if not m_r.empty:
						self.assertIn(m_r, cell.morphemes)
				for m_c in c.morphemes:
					if not m_c.empty:
						self.assertIn(m_c, cell.morphemes)

	def test_table3d_pm(self):
		u = usl("l.-T:.U:.-',n.-T:.A:.-',b.-S:.A:.-'U:.-'U:.-',_ m1(E:S:.x.- S:.E:A:S:.- T:.E:A:T:.-) m1(u.A:.- a.S:.- t.o.-c.-' k.i.-t.i.-t.u.-' n.-T:.A:.-' l.-T:.U:.-',n.-T:.A:.-',m.-B:.U:.-'m.-B:.U:.-'E:A:T:.-',_ l.-T:.U:.-',n.-T:.A:.-',d.-S:.U:.-',_) m1(p.E:A:S:.- E:.-U:.d.-l.-')")
		root_group0 = path(">group_0 1")
		# root_group1 = path(">group_1 1")

		table = UslTable2D(u, rows=None, columns=root_group0)

		cells = table.cells
		self.assertTrue(all(len(cells[0]) == len(row) for row in cells))
		dim = (len(cells), len(cells[0]))
		print(dim)
		dim_column = root_group0.deference(u).cardinal

		self.assertEqual((u.cardinal/dim_column, dim_column), dim)

		for c in chain.from_iterable(cells):
			self.assertEqual(c.cardinal, 1)

		all_cells = set(chain.from_iterable(cells))

		self.assertEqual(len(all_cells), dim[0] * dim[1])
		self.assertEqual(set(table.rows), root_group0.deference(u).singular_sequences_set)
		self.assertEqual(set(table.columns), root_group0.deference(u).singular_sequences_set)

		for r, cells_row in zip(table.rows, cells):
			for c, cell in zip(table.columns, cells_row):
				for m_r in r.morphemes:
					if not m_r.empty:
						self.assertIn(m_r, cell.morphemes)
				for m_c in c.morphemes:
					if not m_c.empty:
						self.assertIn(m_c, cell.morphemes)

if __name__ == '__main__':
	unittest.main()
