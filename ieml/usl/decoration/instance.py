from typing import List

from ieml.commons import DecoratedComponent
from ieml.usl.decoration.path import UslPath


class Decoration:
	def __init__(self, path: UslPath, value):
		self.path = path
		self.value = value

	def apply(self, u: DecoratedComponent):
		tgt = self.path.deference(u)
		tgt.set_literal(self.value)


class InstantiatedUSL:
	def __init__(self, u: 'USL', decorations: List[Decoration]):
		# clone usl, remove literals
		from ieml.usl.usl import usl
		self.usl = usl(str(u))

		self.decorations = decorations
		for decoration in self.decorations:
			if not isinstance(decoration, Decoration):
				raise ValueError("Invalid argument for a InstantiatedUSL, expected a Decoration, got a "+\
								 decoration.__class__.__name__)

			decoration.apply(self.usl)

	@staticmethod
	def from_usl(u: 'USL'):
		decorations = []

		for path, value in u.iter_structure_path():
			if value.get_literal():
				decorations.append(Decoration(path, value.get_literal()))

		return InstantiatedUSL(u, decorations)
