from typing import List

from ieml.commons import DecoratedComponent
from ieml.dictionary.script import Script
from ieml.usl import USL
from ieml.usl.decoration.path import UslPath, FlexionPath


class LiteralContext:
	def __init__(self):
		self.stack = []

	def __enter__(self):
		self.stack = []

	def __exit__(self, exc_type, exc_val, exc_tb):
		for s in self.stack:
			s.clear_literal()
		self.stack = []

	def push(self, u):
		self.stack.append(u)

__literal_context =LiteralContext()
def literal_context():
	return __literal_context


class Decoration:
	def __init__(self, path: UslPath, value):
		self.path = path
		self.value = value

	def apply(self, u: DecoratedComponent):
		tgt = self.path.deference(u)
		tgt.set_literal(self.value)

	def __str__(self):
		return '[{} "{}"]'.format(str(self.path), str(self.value).replace('"', r'\"'))

	def __lt__(self, other):
		return (self.path, self.value) < (other.path, other.value)

	def __eq__(self, other):
		return str(self) == str(other)

class InstancedUSL(USL):
	# last in the  list
	syntactic_level = 10

	def __init__(self, u: 'USL', decorations: List[Decoration]):
		super().__init__()
		# clone usl, remove literals
		# from ieml.usl.usl import usl
		self.usl = u
		self.grammatical_class = self.usl.grammatical_class

		self.flexion = False
		with literal_context():
			for decoration in decorations:
				if not isinstance(decoration, Decoration):
					raise ValueError("Invalid argument for a InstantiatedUSL, expected a Decoration, got a "+\
									 decoration.__class__.__name__)

				self.flexion = isinstance(decoration.path, FlexionPath) or self.flexion

				decoration.apply(self.usl)

			self.decorations = InstancedUSL.list_decorations(self.usl, flexion=self.flexion)

	@staticmethod
	def list_decorations(u: USL, flexion=False):
		decorations = []

		for path, value in u.iter_structure_path(flexion):
			if value.get_literal() is not None:
				decorations.append(Decoration(path, value.get_literal()))

		return sorted(decorations)

	@staticmethod
	def from_usl(u: 'USL'):
		return InstancedUSL(u, InstancedUSL.list_decorations(u))

	def __str__(self):
		return "{} {}".format(str(self.usl), ' '.join(map(str, self.decorations))).strip()

	@property
	def empty(self):
		return self.usl.empty

	def check(self):
		# TODO : check value coherency
		return self.usl.check()

	def iter_structure(self, auto_promote_to_USL=False):
		return self.usl.iter_structure(auto_promote_to_USL=auto_promote_to_USL)

	def iter_structure_path(self, flexion=False):
		return self.usl.iter_structure_path(flexion=flexion)

	def do_lt(self, other):
		return self.usl.do_lt(other)

	def _compute_singular_sequences(self):
		res = []
		for ss in self.usl.singular_sequences:
			dec = []
			with literal_context():
				for d in self.decorations:

					if d.path.contained(ss):
						dec.append(d)

				if dec:
					res.append(InstancedUSL(ss, dec))
				else:
					res.append(ss)

		return res

	@property
	def morphemes(self):
		return self.usl.morphemes
