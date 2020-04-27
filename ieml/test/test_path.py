import unittest

import tqdm

from ieml.dictionary.script import Script
from ieml.ieml_database import IEMLDatabase, GitInterface
from ieml.usl import PolyMorpheme, Lexeme, Word
from ieml.usl.decoration.parser.parser import PathParser
from ieml.usl.decoration.path import PolymorphemePath, GroupIndex, FlexionPath, LexemeIndex, LexemePath, RolePath, \
	usl_from_path_values, path
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
		self.check(">constant", PolymorphemePath, usl('S: A:'), PolyMorpheme)
		self.check(">group_0 1>S:", PolymorphemePath, usl('A: m1(S:)'), Script)
		self.check(">group_0 1", PolymorphemePath, usl('m1(S: A:)'), PolyMorpheme)
		self.check(">group_2 1>B:", PolymorphemePath, usl('A: m1(U:) m1(B:) m1(S:)'), Script)
		self.check(">group_1 1>S:", PolymorphemePath, usl('A: m1(U:) m1(S:)'), Script)
		self.check(">group_2 1", PolymorphemePath, usl('A: m1(U:) m1(B:) m1(S:)'), PolyMorpheme)
		self.check(">group_1 1", PolymorphemePath, usl('A: m1(U:) m1(S:)'), PolyMorpheme)

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

		self.check(">role>E:A:. E:A:.>content>group_0 1>S:", RolePath, w, Script)
		self.check(">role>E:A:. E:A:.>content>constant>p.E:A:T:.-", RolePath, w, Script)
		self.check(">role>E:A:. E:A:.>flexion>E:B:.-d.u.-'", RolePath, w, Script)
		self.check(">role>E:A:.>content>constant>m.-B:.A:.-'", RolePath, w, Script)

		u = usl(
			"[! E:B:. ()(k.a.-k.a.-' l.o.-k.o.-') > E:.f.- ()(m1(p.E:A:S:.- p.E:A:B:.- p.E:A:T:.- t.i.-l.i.-' c.-'B:.-'k.o.-t.o.-',))]")

		self.check(">role>E:.f.->content>group_0 1>p.E:A:S:.-", RolePath, u, Script)


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
		# parser = IEMLParser().parse
		gitdb = GitInterface(origin='https://github.com/plevyieml/ieml-language.git')
		gitdb.pull()
		db = IEMLDatabase(folder=gitdb.folder)

		usls = db.list(type=Word, parse=True) + db.list(type=PolyMorpheme, parse=True) + db.list(type=Lexeme, parse=True)
		for u in tqdm.tqdm(usls):
			p_u = list(u.iter_structure_path_by_script_ss())
			res = usl_from_path_values(p_u)
			self.assertEqual(str(u), str(res), "expand_compose_into_paths failed on: " + str(u))

	def test_expand_compose_into_paths_empty_exclamation(self):
		u = usl('[E:A:.  (E:.-n.S:.-\')(b.a.- b.o.-n.o.-s.u.-\' f.a.-b.a.-f.o.-\') > E:A:. E:A:. ()(n.-S:.U:.-\'B:.-\'B:.-\',B:.-\',B:.-\',_ n.-S:.U:.-\'B:.-\'B:.-\',T:.-\',S:.-\',_) > ! E:A:. E:U:. ()]')
		p_u = list(u.iter_structure_path_by_script_ss())
		res = usl_from_path_values(p_u)
		self.assertEqual(str(u), str(res))

	def test_expand_compose_into_paths_pm(self):
		u = usl("E:T:S:. n.-T:.A:.-'")
		p_u = list(u.iter_structure_path_by_script_ss())
		res = usl_from_path_values(p_u)
		self.assertEqual(str(u), str(res))

	def test_expand_compose_into_paths_pm2(self):
		u = usl("s.-S:.U:.-' n.-T:.A:.-' d.-S:.U:.-' m1(E:.-U:.b.-l.-' E:.-U:.f.-l.-') m1(E:.-B:.k.-l.-')")
		p_u = list(u.iter_structure_path_by_script_ss())
		res = usl_from_path_values(p_u)
		self.assertEqual(str(u), str(res))

	def test_has_prefix(self):
		u = usl("[! E:A:.  ()(b.-S:.A:.-'S:.-'S:.-', m1(S: B: T:) m2(y. o. e. u. a. i.)) > E:A:. E:A:. (m1(E:U:T:. E:A:T:. E:S:T:. E:B:T:. E:T:T:.))(k.a.-k.a.-')]")
		p0 = path(">role>! E:A:.>content>group_0 1>S:")
		p0_prefix = path(">role>! E:A:.>content>group_0 1")
		self.assertTrue(p0.has_prefix(p0_prefix))

	def test_usl_from_path(self):
		structure = {">role>! E:A:.>flexion>E:": "E:",
					">role>! E:A:.>content>constant>b.-S:.A:.-'S:.-'S:.-',": "b.-S:.A:.-'S:.-'S:.-',",
					">role>E:A:. E:A:.>flexion>E:": "E:",
					">role>E:A:. E:A:.>flexion>E:U:T:.": "E:U:T:.",
					">role>E:A:. E:A:.>flexion>E:A:T:.": "E:A:T:.",
					">role>E:A:. E:A:.>flexion>E:S:T:.": "E:S:T:.",
					">role>E:A:. E:A:.>flexion>E:B:T:.": "E:B:T:.",
					">role>E:A:. E:A:.>flexion>E:T:T:.": "E:T:T:.",
					">role>E:A:. E:A:.>content>constant>k.a.-k.a.-'": "k.a.-k.a.-'"}
		usl_parser = IEMLParser().parse
		path_parser = PathParser().parse

		structure = [(path_parser(p), usl_parser(u)) for p, u in structure.items()]

		u = usl_from_path_values(structure)
		self.assertEqual(u, usl("[! E:A:.  ()(b.-S:.A:.-'S:.-'S:.-',) > E:A:. E:A:. (m1(E:U:T:. E:A:T:. E:S:T:. E:B:T:. E:T:T:.))(k.a.-k.a.-')]"))


	def test_usl_from_path_pm(self):
		structure = [
			(">constant>b.-S:.A:.-'S:.-'S:.-',", "b.-S:.A:.-'S:.-'S:.-',"),
			(">constant>k.a.-k.a.-'", "k.a.-k.a.-'"),
			(">constant", "U:"),
			(">constant", "E:")
		]
		usl_parser = IEMLParser().parse
		path_parser = PathParser().parse

		structure = [(path_parser(p), usl_parser(u)) for p, u in structure]

		u = usl_from_path_values(structure)
		self.assertEqual(str(u), "U: k.a.-k.a.-' b.-S:.A:.-'S:.-'S:.-',")

	def test_usl_from_path_flexion_paradigm(self):
		structure = [
			(">flexion", "E:.wo.U:.-t.o.-'"),
			(">flexion", "E:.wo.A:.-t.o.-'"),
			(">content>constant", "U:"),
		]
		usl_parser = IEMLParser().parse
		path_parser = PathParser().parse

		structure = [(path_parser(p), usl_parser(u)) for p, u in structure]

		u = usl_from_path_values(structure)
		self.assertEqual(str(u), "(m1(E:.wo.U:.-t.o.-' E:.wo.A:.-t.o.-'))(U:)")


	def test_usl_from_path_pm2(self):
		structure = [
			(">constant>b.-S:.A:.-'S:.-'S:.-',", "b.-S:.A:.-'S:.-'S:.-',"),
			(">constant", "k.a.-k.a.-' A:"),
			(">constant", "U:"),
			(">constant", "E:")
		]
		usl_parser = IEMLParser().parse
		path_parser = PathParser().parse

		structure = [(path_parser(p), usl_parser(u)) for p, u in structure]

		u = usl_from_path_values(structure)
		self.assertEqual(str(u), "U: A: k.a.-k.a.-' b.-S:.A:.-'S:.-'S:.-',")



if __name__ == '__main__':
	unittest.main()
