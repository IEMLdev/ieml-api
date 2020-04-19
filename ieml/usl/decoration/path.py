from collections import defaultdict
from itertools import chain

from ieml.commons import OrderedEnum, monitor_decorator
from ieml.dictionary.script import Script
from ieml.usl.constants import FLEXION_SCRIPTS
from ieml.usl.syntagmatic_function import SyntagmaticFunction, SyntagmaticRole
from ieml.usl.usl import USL
from ieml.usl.polymorpheme import PolyMorpheme
from ieml.usl.lexeme import Lexeme
from ieml.usl.variation import PolyMorphemeVariation
from ieml.usl.word import Word


class DeferenceError(KeyError):
	pass


SEPARATOR = '>'


def path(string) -> 'UslPath':
	from ieml.usl.decoration.parser.parser import PathParser

	return PathParser().parse(string)


class UslPath:
	USL_TYPE = USL

	def __init__(self, child=None):
		if child is not None:
			if not isinstance(child, UslPath):
				raise ValueError("Invalid path child, expected a UslPath, got a "+ child.__class__.__type__)

		self.child = child

	def _deference(self, usl):
		return usl

	def has_prefix(self, prefix: 'UslPath'):
		if prefix is None:
			return True

		if self.__class__ != prefix.__class__ or (self.__class__ == prefix.__class__ and not self._do_eq(prefix)):
			return self._has_prefix(prefix)

		if self.child is None:
			return prefix.child is None

		return self.child.has_prefix(prefix.child)

	def _has_prefix(self, other):
		return False

	def as_constant(self, u=None):
		return UslPath(child=None if self.child is None else self.child.as_constant(u))

	def remove_prefix(self, prefix: 'UslPath'):
		if not self.has_prefix(prefix):
			return None

		if prefix is None:
			return self

		if not isinstance(self, prefix.__class__) or not self._do_eq(prefix):
			return None

		if self.child is None:
			return None

		return self.child.remove_prefix(prefix.child)

	@property
	def tail(self):
		last = self
		while last.child is not None:
			last = last.child
		return last

	def deference(self, usl: USL) -> USL:
		from ieml.usl.decoration.instance import InstancedUSL

		if isinstance(usl, InstancedUSL):
			usl = usl.usl

		if not isinstance(usl, self.USL_TYPE):
			raise DeferenceError("Invalid Usl type for a " + self.__class__.__name__ + \
											", expected a " + self.USL_TYPE.__name__ + \
											", got a " + usl.__class__.__name__)

		node = self._deference(usl)

		if self.child is not None:
			return self.child.deference(node)
		else:
			return node

	def contained(self, usl):
		try:
			self.deference(usl)
			return True
		except DeferenceError:
			return False

	def _to_str(self):
		return ''

	def __str__(self):
		return SEPARATOR + self._to_str() + (str(self.child) if self.child is not None else '')

	@staticmethod
	def _from_string(string, children):
		return UslPath()

	@classmethod
	def from_string(cls, string):
		if string == SEPARATOR:
			return UslPath._from_string(string, None)

		split = string.split(SEPARATOR)
		return cls._from_string(split[1], split[2:])

	def __eq__(self, other):
		return isinstance(other, UslPath) and str(other) == str(self)

	def __lt__(self, other):
		return self._do_lt(other)

	def _do_eq(self, other):
		return True

	def _do_lt(self, other):
		return False

	def __hash__(self):
		return hash(str(self))

	def no_child_clone(self):
		return UslPath()

	@classmethod
	def build_usl_from_path_to_node(cls, path_to_node):
		raise NotImplementedError()

	@property
	def is_constant_path(self):
		if self.child is not None:
			return self._is_constant_path and self.child.is_constant_path
		else:
			return self._is_constant_path

	@property
	def _is_constant_path(self):
		return False


class GroupIndex(OrderedEnum):
	CONSTANT = -1
	GROUP_0 = 0
	GROUP_1 = 1
	GROUP_2 = 2


class PolymorphemePath(UslPath):
	USL_TYPE = PolyMorpheme

	def __init__(self, group_idx: GroupIndex, morpheme: Script=None, multiplicity=None, child=None):
		super().__init__(child=child)
		self.group_idx = group_idx
		self.morpheme = morpheme
		self.multiplicity = multiplicity

	@property
	def _is_constant_path(self):
		return self.group_idx == GroupIndex.CONSTANT

	def _do_eq(self, other):
		return self.group_idx == other.group_idx and self.morpheme == other.morpheme and \
			   self.multiplicity == other.multiplicity

	def _has_prefix(self, other):
		return self.group_idx == other.group_idx and self.multiplicity == other.multiplicity

	def as_constant(self, u=None):
		return PolymorphemePath(group_idx=GroupIndex.CONSTANT,
								morpheme=self.morpheme if self.morpheme is not None else u,
								multiplicity=None,
								child=(None if self.child is None else self.child.as_constant(u)))


	def _do_lt(self, other):
		return (self.group_idx, self.morpheme) < (other.group_idx, other.morpheme)

	def _deference(self: 'PolymorphemePath', usl: PolyMorpheme):
		if self.group_idx != GroupIndex.CONSTANT and self.group_idx.value >= len(usl.groups):
			raise DeferenceError("Group index " + str(self.group_idx.name) + " not in polymorpheme")

		if self.morpheme is not None:
			if self.group_idx == GroupIndex.CONSTANT:
				group = usl.constant
			else:
				group = usl.groups[self.group_idx.value][0]

			if self.morpheme not in group:
				raise DeferenceError("Morpheme " + str(self.morpheme) + " not in group at " + str(self.group_idx.name))

			return self.morpheme
		else:
			if self.group_idx == GroupIndex.CONSTANT:
				return PolyMorpheme(constant=usl.constant)
			else:
				return usl.groups_paradigms[self.group_idx.value]

	def _to_str(self):
		if self.group_idx == GroupIndex.CONSTANT:
			if self.morpheme is not None:
				return 'constant' + SEPARATOR + str(self.morpheme)
			else:
				return 'constant'
		else:
			if self.morpheme is not None:
				return 'group_{}'.format(self.group_idx.value) + \
					(' {}'.format(self.multiplicity) if self.multiplicity is not None else '') + \
					SEPARATOR + str(self.morpheme)
			else:
				return 'group_{}'.format(self.group_idx.value) + \
					(' {}'.format(self.multiplicity) if self.multiplicity is not None else '')

	@staticmethod
	def _from_string(elem, children):
		if elem == '':
			return UslPath()

		key = elem
		morph = None
		if len(children) == 1:
			from ieml.usl.usl import usl
			morph = usl(children[0])

		idx = None
		multiplicity = None

		if key.startswith('constant'):
			idx = GroupIndex.CONSTANT
		elif key.startswith('group_'):
			if ' ' in key:
				key_, multi = key.split(' ')
				multiplicity = int(multi)
			else:
				key_ = key

			n = int(''.join(key_[6:]))

			if n == 0:
				idx = GroupIndex.GROUP_0
			elif n == 1:
				idx = GroupIndex.GROUP_1
			elif n == 2:
				idx = GroupIndex.GROUP_2
			else:
				raise ValueError("Invalid argument index for a PolymorphemePath _from_string constructor: " + str(n))
		else:
			raise ValueError("Invalid argument for a PolymorphemePath _from_string constructor: " + key)

		return PolymorphemePath(group_idx=idx, morpheme=morph, multiplicity=multiplicity)

	def no_child_clone(self):
		return PolymorphemePath(group_idx=self.group_idx, morpheme=self.morpheme, multiplicity=self.multiplicity)

	@classmethod
	def build_usl_from_path_to_node(cls, path_to_node):
		"""
		path_to_node: dict PolymorphemePath -> Script
		# TODO handle multiplicity 
		:param path_to_node:
		:return:
		"""

		expend_values = lambda e: [e] if isinstance(e, Script) else e.constant

		constant = []
		groups = [[[], None],[[], None],[[], None]]

		for k, values in path_to_node.items():
			if not isinstance(k, PolymorphemePath):
				raise ValueError("invalid path type to instantiate a polymorphem " + k.__class__.__name__)

			if k.group_idx == GroupIndex.CONSTANT:
				constant.extend(chain.from_iterable(map(expend_values, values)))
			else:
				if k.group_idx == GroupIndex.GROUP_0:
					idx = 0
				elif k.group_idx == GroupIndex.GROUP_1:
					idx = 1
				elif k.group_idx == GroupIndex.GROUP_2:
					idx = 2
				else:
					raise ValueError("Invalid polymorpheme path " + str(k))

				groups[idx][0].extend(chain.from_iterable(map(expend_values, values)))
				if k.multiplicity:
					if groups[idx][1] is not None and k.multiplicity != groups[idx][1]:
						raise ValueError("Incoherent multiplicity across the path")

					groups[idx][1] = k.multiplicity
				else:
					groups[idx][1] = 1

		groups = [g for g in groups if g[0] != []]
		return PolyMorpheme(constant=constant, groups=groups)


class FlexionPath(UslPath):
	USL_TYPE = PolyMorpheme

	def __init__(self, morpheme, child=None):
		super().__init__(child=child)
		from ieml.dictionary.script import Script

		assert isinstance(morpheme, Script)
		self.morpheme = morpheme

	@property
	def _is_constant_path(self):
		return True

	def as_constant(self, u=None):
		return FlexionPath(morpheme=self.morpheme,
						   child=(None if self.child is None else self.child.as_constant(u)))

	def _do_eq(self, other):
		return self.morpheme == other.morpheme

	def _do_lt(self, other):
		return self.morpheme < other.morpheme

	def _deference(self: 'FlexionPath', usl: PolyMorpheme):
		all_group = [usl.constant, *(list(filter(lambda m: not m.empty, g)) for g, _ in usl.groups)]
		all_morphemes = {str(w): w for g in all_group for w in g}

		if self.morpheme not in all_morphemes:
			raise DeferenceError("Morpheme " + str(self.morpheme) + " not in flexion")

		return self.morpheme

	def _to_str(self):
		return str(self.morpheme)

	@staticmethod
	def _from_string(elem, children):
		if elem == '':
			return UslPath()

		from ieml.usl.usl import usl

		morph = usl(elem)
		assert len(children) == 0
		return FlexionPath(morpheme=morph)

	def no_child_clone(self):
		return FlexionPath(morpheme=self.morpheme)

	@classmethod
	def build_usl_from_path_to_node(cls, path_to_node):
		all_morphemes = []
		for k, values in path_to_node.items():
			if not isinstance(k, FlexionPath):
				raise ValueError("invalid path type to instantiate a polymorphem " + k.__class__.__name__)

			all_morphemes.extend(values)

		root_flexion_groups = defaultdict(set)

		for m in all_morphemes:
			for r in FLEXION_SCRIPTS:
				if m in r.singular_sequences_set:
					root_flexion_groups[r].add(m)

		constant = []
		groups = []

		for k, v in root_flexion_groups.items():
			if len(v) == 0:
				continue
			elif len(v) == 1:
				constant.append(next(iter(v)))
			else:
				groups.append([list(v), 1])

		return PolyMorpheme(constant=constant, groups=groups)


class LexemeIndex(OrderedEnum):
	CONTENT = 0
	FLEXION = 1


class LexemePath(UslPath):
	USL_TYPE = Lexeme

	def __init__(self, index: LexemeIndex, child=None):
		super().__init__(child=child)
		assert isinstance(index, LexemeIndex)
		self.index = index

		if child is not None and not child.__class__ == UslPath:
			if self.index == LexemeIndex.CONTENT:
				assert isinstance(self.child, PolymorphemePath), \
					"Invalid path structure, a lexeme content child must be a PolymorphemePath, not a " + self.child.__class__.__name__
			else:
				assert isinstance(self.child, FlexionPath), \
					"Invalid path structure, a lexeme flexion child must be a FlexionPath, not a " + self.child.__class__.__name__

	def as_constant(self, u=None):
		return LexemePath(index=self.index,
						  child=(None if self.child is None else self.child.as_constant(u)))

	@property
	def _is_constant_path(self):
		return True

	def _do_eq(self, other):
		return self.index == other.index

	def _do_lt(self, other):
		return self.index < other.index

	def _deference(self: 'LexemePath', usl: Lexeme):
		if self.index == LexemeIndex.CONTENT:
			return usl.pm_content
		else:
			return usl.pm_flexion

	def _to_str(self):
		if self.index == LexemeIndex.CONTENT:
			return 'content'
		else:
			return 'flexion'

	@staticmethod
	def _from_string(elem, children):
		if elem == '':
			return UslPath()

		idx = None
		if elem == 'content':
			idx = LexemeIndex.CONTENT
		elif elem == 'flexion':
			idx = LexemeIndex.FLEXION
		else:
			raise ValueError("Invalid argument for a LexemePath _from_string constructor: " + elem)

		child = None
		if len(children) != 0:
			if idx == LexemeIndex.CONTENT:
				child = PolymorphemePath._from_string(children[0], children[1:])
			else:
				child = FlexionPath._from_string(children[0], children[1:])

		return LexemePath(index=idx, child=child)

	def no_child_clone(self):
		return LexemePath(index=self.index)

	@classmethod
	def build_usl_from_path_to_node(cls, path_to_node):
		pm_content = None
		pm_flexion = None
		
		for k, v in path_to_node.items():
			if not isinstance(k, LexemePath):
				raise ValueError("invalid path type to instantiate a Lexeme " + k.__class__.__name__)
			
			if k.index == LexemeIndex.CONTENT:
				if pm_content is not None:
					raise ValueError("Multiple candidates for the content of the Lexeme")

				pm_content = v
			elif k.index == LexemeIndex.FLEXION:
				if pm_flexion is not None:
					raise ValueError("Multiple candidates for the flexion of the Lexeme")

				pm_flexion = v

		if pm_content is None:
			pm_content = PolyMorpheme([])

		if pm_flexion is None:
			pm_flexion = PolyMorpheme([])


		return Lexeme(pm_content=pm_content, pm_flexion=pm_flexion)


class RolePath(UslPath):
	USL_TYPE = Word

	def __init__(self, role, has_focus=False, child=None):
		super().__init__(child)
		from ieml.usl.syntagmatic_function import SyntagmaticRole

		if not isinstance(role, SyntagmaticRole):
			raise DeferenceError("Invalid role for a RolePath " + role.__class__.__name__)

		self.role = role

		if child is not None and not child.__class__ == UslPath:
			if not isinstance(child, LexemePath):
				raise DeferenceError("Invalid path structure, a lexeme content child must be a PolymorphemePath, not a " + self.child.__class__.__name__)

		self.has_focus = has_focus

	def as_constant(self, u=None):
		return RolePath(role=self.role,
						has_focus=self.has_focus,
						child=(None if self.child is None else self.child.as_constant(u)))

	@property
	def _is_constant_path(self):
		return True

	def _do_eq(self, other):
		return self.role == other.role and self.has_focus == other.has_focus

	def _do_lt(self, other):
		return self.role < other.role

	def _deference(self: 'RolePath', usl: Word):
		try:
			return usl.syntagmatic_fun.get(self.role, ignore_prefix=True, ignore_process_valence=True)
		except KeyError as key:
			raise DeferenceError(key)

	def _to_str(self):
		return 'role' + SEPARATOR + ('! ' if self.has_focus else '') + str(self.role)

	@staticmethod
	def _from_string(elem, children):
		from ieml.usl.syntagmatic_function import SyntagmaticRole

		if elem == '':
			if len(children) == 0:
				return UslPath()

			raise ValueError("Empty role in RolePath")

		from ieml.usl.usl import usl

		sfun_role = SyntagmaticRole([usl(s) for s in elem.split(' ') if s != '!'])

		child = None
		if len(children) != 0:
			child = LexemePath._from_string(children[0], children[1:])

		return RolePath(role=sfun_role, has_focus='!' in elem,child=child)

	def no_child_clone(self):
		return RolePath(role=self.role, has_focus=self.has_focus)

	@classmethod
	def build_usl_from_path_to_node(cls, path_to_node):
		focus_role = None

		for k, v in path_to_node.items():
			if not isinstance(k, RolePath):
				raise ValueError("invalid path type to instantiate a Word " + k.__class__.__name__)

			if k.has_focus:
				if focus_role is not None and focus_role != k.role:
					raise ValueError("Incoherent focus role, multiple differents values")
				focus_role = k.role

		lex_list = [(k.role.constant, v) for k, v in path_to_node.items()]

		ctx_type, sfun = SyntagmaticFunction.from_list(lex_list)

		if focus_role is None:
			raise ValueError("No focus role defined in this word")

		return Word(syntagmatic_fun=sfun,
					role=focus_role,
					context_type=ctx_type)


# @monitor_decorator('usl_from_path_values')
def usl_from_path_values(paths_values):
	from ieml.usl.decoration.parser.parser import PathParser
	from ieml.usl.parser import IEMLParser

	path_parser = PathParser()
	usl_parser = IEMLParser()

	path_to_value = {path_parser.parse(p): [] for p, _ in paths_values}
	for p, v in paths_values:
		path_to_value[path_parser.parse(p)].append(usl_parser.parse(v))

	x = lambda : defaultdict(x)
	bins = x()

	def recursive_group_by(bin, path, values):
		p_cloned = path.no_child_clone()

		if 'type' in bin:
			if not isinstance(path, bin['type']):
				raise ValueError("Inconsistent path system")
		else:
			bin['type'] = path.__class__

		if path.child is None:
			bin[p_cloned]["node"] = values
		else:
			recursive_group_by(bin[p_cloned], path.child, values)

	def build_nodes(bin):
		if 'node' not in bin:
			path_to_node = {}
			for p, bin_child in bin.items():
				if isinstance(p, UslPath):
					path_to_node[p] = build_nodes(bin_child)

			assert 'type' in bin
			bin['node'] = bin['type'].build_usl_from_path_to_node(path_to_node)

		return bin['node']

	for p, values in path_to_value.items():
		recursive_group_by(bins, p, values)

	return build_nodes(bins)