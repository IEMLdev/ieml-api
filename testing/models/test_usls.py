import random
import string

from ieml.usl import random_usl
from models.usl.usl import usl_index
from testing.models.stub_db import ModelTestCase


class TestUSLsModel(ModelTestCase):
    def save_random_usl(self):
        rand_string = lambda : ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))

        _usl = random_usl()
        tags = {'FR': rand_string(), 'EN': rand_string()}
        keywords = {'FR': [rand_string() for i in range(random.randint(1, 5))], 'EN': [rand_string() for i in range(random.randint(1, 5))]}
        self.usls.save_usl(_usl, tags=tags, keywords=keywords)

        return {
            '_id': usl_index(_usl),
            'IEML': str(_usl),
            'TAGS': tags,
            'KEYWORDS': keywords
        }

    def test_add_usl(self):
        _entry = self.save_random_usl()

        self.assertEqual(list(self.usls.usls.find())[0], _entry, "Entry in db doesn't match.")

    def test_get_usl(self):
        _entry = self.save_random_usl()

        self.assertEqual(_entry, self.usls.get_usl(_entry['_id']))

    def test_remove_usl(self):
        _entry = self.save_random_usl()

        self.usls.remove_usl(_entry['_id'])
        self.assertEqual(self.usls.usls.count(), 0)

    def test_multi_add(self):
        _entry0 = self.save_random_usl()
        _entry1 = self.save_random_usl()
        _db_entries = sorted(self.usls.usls.find(), key=lambda e: e['_id'])
        _entries = sorted((_entry0, _entry1), key=lambda e: e['_id'])
        for e0, e1 in zip(_entries, _db_entries):
            self.assertDictEqual(e0, e1)

