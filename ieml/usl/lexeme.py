import itertools
from ieml.usl import USL, PolyMorpheme, check_polymorpheme


def check_lexeme(lexeme, sfun=None):
	for pm in [lexeme.pm_flexion, lexeme.pm_content]:
		if not isinstance(pm, PolyMorpheme):
			raise ValueError("Invalid arguments to create a Lexeme, expects a Polymorpheme, not a {}."
							 .format(pm.__class__.__name__))

		check_polymorpheme(pm)

	# check_lexeme_scripts(lexeme.pm_flexion.constant,
	#                      lexeme.pm_content.constant,
	#                      sfun=sfun)


class Lexeme(USL):
	"""A lexeme without the PA of the position on the tree (position independant lexeme)"""

	syntactic_level = 2

	def __init__(self, pm_flexion: PolyMorpheme, pm_content: PolyMorpheme):
		super().__init__()
		self.pm_flexion = pm_flexion
		self.pm_content = pm_content

		# self.address = PolyMorpheme(constant=[m for m in pm_address.constant if m in ADDRESS_SCRIPTS])
		self.grammatical_class = self.pm_content.grammatical_class

		self._str = []
		for pm in [self.pm_content, self.pm_flexion]:
			if not self._str and pm.empty:
				continue
			self._str.append("({})".format(str(pm)))

		self._str = ''.join(reversed(self._str))
		if not self._str:
			self._str = "()"

	def check(self):
		pass

	def iter_structure(self):
		yield self.pm_flexion
		yield from self.pm_flexion.iter_structure()
		yield self.pm_content
		yield from self.pm_content.iter_structure()

	def iter_structure_path(self):
		from ieml.usl.decoration.path import LexemePath, LexemeIndex
		from ieml.usl.decoration.path import FlexionPath

		yield (LexemePath(LexemeIndex.FLEXION), self.pm_flexion)

		yield from [(LexemePath(LexemeIndex.FLEXION, child=FlexionPath(path.morpheme)), pm)
					for path, pm in self.pm_flexion.iter_structure_path()]

		yield (LexemePath(LexemeIndex.CONTENT), self.pm_content)
		yield from [(LexemePath(LexemeIndex.CONTENT, child=path), pm)
					for path, pm in self.pm_content.iter_structure_path()]


	@property
	def empty(self):
		return self.pm_content.empty and self.pm_flexion.empty


	def do_lt(self, other):
		return self.pm_flexion < other.pm_flexion or \
			   (self.pm_flexion == other.pm_flexion and self.pm_content < other.pm_content)


	def _compute_singular_sequences(self):
		if self.pm_flexion.is_singular and (self.pm_content is None or self.pm_content.is_singular):
			return [self]
		else:
			_product = [self.pm_flexion,
						self.pm_content]
			_product = [p.singular_sequences for p in _product if p is not None]

			return [Lexeme(*ss)
					for ss in itertools.product(*_product)]


	@property
	def morphemes(self):
		return sorted(set(self.pm_flexion.morphemes + self.pm_content.morphemes))
