from ieml.usl import PolyMorpheme, USL
from ieml.dictionary.script import Script
from enum import Enum
from ieml.usl.usl import usl

from ieml.usl import Lexeme

from ieml.usl import Word
from ieml.usl.syntagmatic_function import SyntagmaticRole


class UslPath:
	USL_TYPE = USL

	def __init__(self, child=None):
		if child is not None:
			if not isinstance(child, UslPath):
				raise ValueError("Invalid path child, expected a UslPath, got a "+ child.__class__.__type__)

		self.child = child

	def _deference(self, usl):
		return usl

	def deference(self, usl):
		assert isinstance(usl,
						  self.USL_TYPE), "Invalid Usl type for a " + self.__class__.__name__ + ", expected a " + self.USL_TYPE.__name__ + \
										  ", got a " + usl.__class__.__name__

		node = self._deference(usl)

		if self.child is not None:
			return self.child.deference(node)
		else:
			return node

	def _to_str(self):
		return ''

	def __str__(self):
		return '/' + self._to_str() + (str(self.child) if self.child is not None else '')

	@staticmethod
	def _from_string(string, children):
		return UslPath()

	@classmethod
	def from_string(cls, string):
		if string == '/':
			return UslPath._from_string(string, None)

		split = string.split('/')
		return cls._from_string(split[1], split[2:])


class GroupIndex(Enum):
	CONSTANT = -1
	GROUP_0 = 0
	GROUP_1 = 1
	GROUP_2 = 2


class PolymorphemePath(UslPath):
	USL_TYPE = PolyMorpheme

	def __init__(self, group_idx: GroupIndex, morpheme: Script, child=None):
		super().__init__(child=child)
		self.group_idx = group_idx
		self.morpheme = morpheme

	def _deference(self: 'PolymorphemePath', usl: PolyMorpheme):
		group = None

		if self.group_idx == GroupIndex.CONSTANT:
			group = usl.constant
		else:
			assert self.group_idx.value < len(usl.groups)
			group = usl.groups[self.group_idx.value][0]

		assert self.morpheme in group

		return self.morpheme

	def _to_str(self):
		if self.group_idx == GroupIndex.CONSTANT:
			return 'constant/' + str(self.morpheme)
		else:
			return 'group_{}/'.format(self.group_idx.value) + str(self.morpheme)

	@staticmethod
	def _from_string(elem, children):
		if elem == '':
			return UslPath()

		key = elem
		assert len(children) == 1, '[{:s}]'.format(" ".join(map(str, children)))
		morph = children[0]

		idx = None
		if key.startswith('constant'):
			idx = GroupIndex.CONSTANT
		elif key.startswith('group_'):
			n = int(''.join(key[6:]))
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

		morph = usl(morph)
		return PolymorphemePath(group_idx=idx, morpheme=morph)




class FlexionPath(UslPath):
	USL_TYPE = PolyMorpheme

	def __init__(self, morpheme: Script, child=None):
		super().__init__(child=child)
		assert isinstance(morpheme, Script)
		self.morpheme = morpheme

	def _deference(self: 'FlexionPath', usl: PolyMorpheme):
		all_group = [usl.constant, *(list(filter(lambda m: not m.empty, g)) for g, _ in usl.groups)]
		all_morphemes = {str(w): w for g in all_group for w in g}

		assert self.morpheme in all_morphemes
		return self.morpheme

	def _to_str(self):
		return str(self.morpheme)

	@staticmethod
	def _from_string(elem, children):
		if elem == '':
			return UslPath()

		morph = usl(elem)
		assert len(children) == 0
		return FlexionPath(morpheme=morph)


class LexemeIndex(Enum):
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


class RolePath(UslPath):
	USL_TYPE = Word

	def __init__(self, role, child=None):
		super().__init__(child)
		assert isinstance(role, SyntagmaticRole)

		self.role = role

		if child is not None and not child.__class__ == UslPath:
			if not isinstance(child, LexemePath):
				raise ValueError("Invalid path structure, a lexeme content child must be a PolymorphemePath, not a " + self.child.__class__.__name__)

	def _deference(self: 'RolePath', usl: Word):
		return usl.syntagmatic_fun.get(self.role)

	def _to_str(self):
		return str(self.role)

	@staticmethod
	def _from_string(elem, children):
		if elem == '':
			if len(children) == 0:
				return UslPath()

			sfun_role = SyntagmaticRole([])
		else:
			sfun_role = SyntagmaticRole([usl(s) for s in elem.split(' ')])

		child = None
		if len(children) != 0:
			child = LexemePath._from_string(children[0], children[1:])

		return RolePath(role=sfun_role, child=child)

