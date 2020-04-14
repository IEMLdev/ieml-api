import unittest

import tqdm

from ieml.dictionary.script import Script
from ieml.ieml_database import IEMLDatabase, GitInterface
from ieml.usl import PolyMorpheme, Lexeme, Word
from ieml.usl.decoration.parser.parser import PathParser
from ieml.usl.decoration.path import PolymorphemePath, GroupIndex, FlexionPath, LexemeIndex, LexemePath, RolePath, \
	usl_from_path_values
from ieml.usl.parser import IEMLParser
from ieml.usl.syntagmatic_function import SyntagmaticRole
from ieml.usl.usl import usl

parser = PathParser()
class TestPath(unittest.TestCase):

	def check(self, path, _type, usl, expected_type):

		self.assertEqual(str(parser.parse(path)), path)

		res = parser.parse(path).deference(usl)
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

		self.check(">constant>S:", PolymorphemePath, usl('S: A:'), Script)
		self.check(">group_0>S:", PolymorphemePath, usl('A: m1(S:)'), Script)
		self.check(">group_2>B:", PolymorphemePath, usl('A: m1(U:) m1(B:) m1(S:)'), Script)
		self.check(">group_1>S:", PolymorphemePath, usl('A: m1(U:) m1(S:)'), Script)

		self.check(">", PolymorphemePath, usl('S: A:'), PolyMorpheme)

		LexemePath(LexemeIndex.CONTENT, child=PolymorphemePath(GroupIndex.CONSTANT, usl('S:'))).deference(
			usl("()(S: B:)"))
		LexemePath(LexemeIndex.FLEXION, child=FlexionPath(usl('S:'))).deference(usl("(S: B:)(S:)"))

		self.check('>content>constant>S:', LexemePath, usl('()(S:)'), Script)
		self.check('>flexion>S:', LexemePath, usl('(S:)(B:)'), Script)
		self.check('>flexion', LexemePath, usl('(S:)(B:)'), PolyMorpheme)

		self.check('>flexion', LexemePath, usl('(S:)(B:)'), PolyMorpheme)
		self.check(">", LexemePath, usl('(S:)(B:)'), Lexeme)

		w = usl("[! E:A:. ()(m.-B:.A:.-') > E:A:. E:A:. (E:B:.-d.u.-')(p.E:A:T:.- m1(S:))]")
		path = RolePath(SyntagmaticRole([usl('E:A:.'), usl('E:A:.')]),
						child=LexemePath(LexemeIndex.CONTENT,
										 child=PolymorphemePath(GroupIndex.CONSTANT, usl('p.E:A:T:.-'))))
		path.deference(w)

		self.check(">role>E:A:. E:A:.>content>group_0>S:", RolePath, w, Script)
		self.check(">role>E:A:. E:A:.>content>constant>p.E:A:T:.-", RolePath, w, Script)
		self.check(">role>E:A:. E:A:.>flexion>E:B:.-d.u.-'", RolePath, w, Script)
		self.check(">role>E:A:.>content>constant>m.-B:.A:.-'", RolePath, w, Script)

		self.check(">role>E:A:.", RolePath, w, Lexeme)
		self.check(">role>E:A:.>content", RolePath, w, PolyMorpheme)
		self.check(">", RolePath, w, Word)

	def test_paths_values_to_usl(self):
		pm = [(">constant>S:", "S:"), (">constant>B:", "B:"), (">group_0 2>T:", "T:"), (">group_0 2>A:", "A:")]
		res = usl_from_path_values(pm)
		self.assertIsInstance(res, PolyMorpheme)
		self.assertEqual(str(res), "S: B: m2(A: T:)")

		pm = [(">content>constant>S:", "S:"), (">content>constant>B:", "B:"), (">content>group_0 1>T:", "T:")]
		res = usl_from_path_values(pm)
		self.assertIsInstance(res, Lexeme)
		self.assertEqual(str(res), "()(S: B: m1(T:))")

		pm = [(">role>! E:A:.>content>constant>S:", "S:"),
			  (">role>E:A:. E:A:.>content>constant>B:", "B:"),
			  (">role>E:A:. E:A:.>content>group_0>T:", "T:")]
		res = usl_from_path_values(pm)
		self.assertIsInstance(res, Word)
		self.assertEqual(str(res), "[! E:A:.  ()(S:) > E:A:. E:A:. ()(B: m1(T:))]")

	def test_expand_compose_into_paths(self):
		parser = IEMLParser().parse
		gitdb = GitInterface()
		gitdb.pull()
		db = IEMLDatabase(folder=gitdb.folder)

		usls = db.list(type=Word, parse=True) + db.list(type=PolyMorpheme, parse=True)
		for u in tqdm.tqdm(usls):
			p_u = list(u.iter_structure_path_by_type(Script))
			res = usl_from_path_values(p_u)
			self.assertEqual(str(u), str(res), "expand_compose_into_paths failed on: " + str(u))

	def test_expand_compose_into_paths_empty_exclamation(self):
		u = usl('[E:A:.  (E:.-n.S:.-\')(b.a.- b.o.-n.o.-s.u.-\' f.a.-b.a.-f.o.-\') > E:A:. E:A:. ()(n.-S:.U:.-\'B:.-\'B:.-\',B:.-\',B:.-\',_ n.-S:.U:.-\'B:.-\'B:.-\',T:.-\',S:.-\',_) > ! E:A:. E:U:. ()]')
		p_u = list(u.iter_structure_path_by_type(Script))
		res = usl_from_path_values(p_u)
		self.assertEqual(str(u), str(res))

	def test_expand_compose_into_paths_pm(self):
		u = usl("E:T:S:. n.-T:.A:.-'")
		p_u = list(u.iter_structure_path_by_type(Script))
		res = usl_from_path_values(p_u)
		self.assertEqual(str(u), str(res))


if __name__ == '__main__':
	unittest.main()
