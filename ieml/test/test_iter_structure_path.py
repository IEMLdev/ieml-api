import unittest

from ieml.usl.decoration.instance import InstantiatedUSL
from ieml.usl.decoration.path import path
from ieml.usl.usl import usl


class TestIterStructurePath(unittest.TestCase):
	def test_iter_word(self):
		w = usl("[! E:A:. ()(m.-B:.A:.-') > E:A:. E:A:. (E:B:.-d.u.-')(p.E:A:T:.- m1(S:))]")

		print('\n'.join("{} -> {}".format(str(s), str(v)) for s, v in w.iter_structure_path()))


	def test_instanciated_usl(self):
		w = usl("[! E:A:. ()(m.-B:.A:.-') > E:A:. E:A:. (E:B:.-d.u.-')(p.E:A:T:.- m1(S:))]")

		x = path("/E:A:./content/constant/m.-B:.A:.-'").deference(w)
		x.set_literal("test")

		i_u = InstantiatedUSL.from_usl(w)
		self.assertEqual(i_u.decorations[0].value, 'test')





if __name__ == '__main__':
	unittest.main()
