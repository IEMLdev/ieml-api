import operator
import random
from functools import reduce

from ieml.ieml_objects.texts import Text
from ieml.ieml_objects.words import Word
from ieml.script.constants import CONTAINS_RELATION
from ieml.usl.tools import random_usl
from testing.models.stub_db import ModelTestCase


class TestTemplates(ModelTestCase):
    connectors = 'templates',

    def test_save_templates(self):

        while True:
            try:
                u = random_usl(rank_type=Text)
                paths = random.sample([p for p, t in u.paths.items() if t.script.paradigm], 2)
                break
            except ValueError:
                continue

        self.templates.save_template(u, paths)
        entry = self.templates.get_template(u)
        self.assertEqual(entry['IEML'], str(u))
