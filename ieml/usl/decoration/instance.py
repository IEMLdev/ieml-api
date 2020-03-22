from typing import List

from ieml.commons import DecoratedComponent
from ieml.usl import USL
from ieml.usl.decoration.path import UslPath


class Decoration:
	def __init__(self, path: UslPath, value):
		self.path = path
		self.value = value

	def apply(self, u: DecoratedComponent):
		tgt = self.path.deference(u)
		tgt.set_literal(self.value)

	def __str__(self):
		return '[{} "{}"]'.format(str(self.path), str(self.value))


class InstancedUSL(USL):
	# last in the  list
	syntactic_level = 10

	def __init__(self, u: 'USL', decorations: List[Decoration]):
		super().__init__()
		# clone usl, remove literals
		# from ieml.usl.usl import usl
		self.usl = u
		self.grammatical_class = self.usl.grammatical_class

		for decoration in decorations:
			if not isinstance(decoration, Decoration):
				raise ValueError("Invalid argument for a InstantiatedUSL, expected a Decoration, got a "+\
								 decoration.__class__.__name__)

			decoration.apply(self.usl)

		self.decorations = InstancedUSL.list_decorations(self.usl)

	@staticmethod
	def list_decorations(u: USL):
		decorations = []

		for path, value in u.iter_structure_path():
			if value.get_literal():
				decorations.append(Decoration(path, value.get_literal()))

		return decorations

	@staticmethod
	def from_usl(u: 'USL'):
		return InstancedUSL(u, InstancedUSL.list_decorations(u))

	def __str__(self):
		return "{} {}".format(str(self.usl), ' '.join(map(str, self.decorations)))

	@property
	def empty(self):
		return self.usl.empty

	def check(self):
		# TODO : check value coherency
		return self.usl.check()

	def iter_structure(self):
		return self.usl.iter_structure()

	def iter_structure_path(self):
		return self.usl.iter_structure_path()

	def _compute_singular_sequences(self):
		return self.usl.singular_sequences

	@property
	def morphemes(self):
		return self.usl.morphemes
