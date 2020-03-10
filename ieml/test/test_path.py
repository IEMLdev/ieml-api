import unittest

from ieml.dictionary.script import Script
from ieml.usl import PolyMorpheme, Lexeme, Word
from ieml.usl.decoration.path import PolymorphemePath, GroupIndex, FlexionPath, LexemeIndex, LexemePath, RolePath
from ieml.usl.syntagmatic_function import SyntagmaticRole


class TestPath(unittest.TestCase):

	def check(self, path, _type, usl, expected_type):

		self.assertEqual(str(_type.from_string(path)), path)

		res = _type.from_string(path).deference(usl)
		self.assertIsInstance(res, expected_type)

	def test_path(self):
		from ieml.usl.usl import usl
		pm = [usl("A: E: S: B: T:"), usl("A: E: m1(S: B: T:)"), usl("A: m1(E:) m1(S: B: T:)"),
			  usl("m1(A:) m1(E:) m1(S: B: T:)")]

		# pm_path = PolymorphemePath(GroupIndex.CONSTANT, usl('S:'))
		PolymorphemePath(GroupIndex.CONSTANT, usl('S:')).deference(pm[0])
		PolymorphemePath(GroupIndex.GROUP_0, usl('S:')).deference(pm[1])
		PolymorphemePath(GroupIndex.GROUP_1, usl('S:')).deference(pm[2])
		PolymorphemePath(GroupIndex.GROUP_2, usl('S:')).deference(pm[3])

		self.check("/constant/S:", PolymorphemePath, usl('S: A:'), Script)
		self.check("/group_0/S:", PolymorphemePath, usl('A: m1(S:)'), Script)
		self.check("/group_2/B:", PolymorphemePath, usl('A: m1(U:) m1(B:) m1(S:)'), Script)
		self.check("/group_1/S:", PolymorphemePath, usl('A: m1(U:) m1(S:)'), Script)

		self.check("/", PolymorphemePath, usl('S: A:'), PolyMorpheme)

		LexemePath(LexemeIndex.CONTENT, child=PolymorphemePath(GroupIndex.CONSTANT, usl('S:'))).deference(
			usl("()(S: B:)"))
		LexemePath(LexemeIndex.FLEXION, child=FlexionPath(usl('S:'))).deference(usl("(S: B:)(S:)"))

		self.check('/content/constant/S:', LexemePath, usl('()(S:)'), Script)
		self.check('/flexion/S:', LexemePath, usl('(S:)(B:)'), Script)
		self.check('/flexion', LexemePath, usl('(S:)(B:)'), PolyMorpheme)

		self.check('/flexion', LexemePath, usl('(S:)(B:)'), PolyMorpheme)
		self.check("/", LexemePath, usl('(S:)(B:)'), Lexeme)


		w = usl("[! E:A:. ()(m.-B:.A:.-') > E:A:. E:A:. (E:B:.-d.u.-')(p.E:A:T:.- m1(S:))]")
		path = RolePath(SyntagmaticRole([usl('E:A:.')]),
						child=LexemePath(LexemeIndex.CONTENT,
										 child=PolymorphemePath(GroupIndex.CONSTANT, usl('p.E:A:T:.-'))))
		path.deference(w)

		self.check("/E:A:./content/group_0/S:", RolePath, w, Script)
		self.check("/E:A:./content/constant/p.E:A:T:.-", RolePath, w, Script)
		self.check("/E:A:./flexion/E:B:.-d.u.-'", RolePath, w, Script)
		self.check("//content/constant/m.-B:.A:.-'", RolePath, w, Script)

		self.check("//", RolePath, w, Lexeme)
		self.check("//content/", RolePath, w, PolyMorpheme)
		self.check("/", RolePath, w, Word)

if __name__ == '__main__':
	unittest.main()
