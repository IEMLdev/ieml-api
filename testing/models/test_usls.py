import random
import string

from ieml.ieml_objects.texts import Text
from ieml.usl import random_usl
from models.constants import TAG_LANGUAGES
from models.usls.usls import usl_index
from testing.models.stub_db import ModelTestCase


class TestUSLsModel(ModelTestCase):

    connectors = ('usls',)

    def save_random_usl(self, tags=None):
        rand_string = lambda : ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))

        _usl = random_usl()
        if not tags:
            tags = {'FR': rand_string(), 'EN': rand_string()}
        keywords = {'FR': [rand_string() for i in range(random.randint(1, 5))], 'EN': [rand_string() for i in range(random.randint(1, 5))]}
        _id = self.usls.save(_usl, tags=tags, keywords=keywords)

        return {
            '_id': _id,
            'USL': {
                'INDEX': usl_index(_usl),
                'IEML': str(_usl)
            },
            'TAGS': tags,
            'KEYWORDS': keywords,
            'TEMPLATES': [],
            'PARENTS': []
        }

    def test_add_usl(self):
        _entry = self.save_random_usl()

        self.assertEqual(list(self.usls.usls.find())[0], _entry, "Entry in db doesn't match.")

    def test_get_usl(self):
        _entry = self.save_random_usl()

        self.assertEqual(_entry, self.usls.get(usl=_entry['USL']['IEML']))
        self.assertEqual(_entry, self.usls.get(id=_entry['_id']))
        self.assertEqual(_entry, self.usls.get(tag=_entry['TAGS']['EN'], language='EN'))

    def test_remove_usl(self):
        _entry = self.save_random_usl()
        self.usls.remove(usl=_entry['USL']['IEML'])
        self.assertEqual(self.usls.usls.count(), 0)

        _entry = self.save_random_usl()
        self.usls.remove(id=_entry['_id'])
        self.assertEqual(self.usls.usls.count(), 0)

    def test_multi_add(self):
        _entry0 = self.save_random_usl()
        _entry1 = self.save_random_usl()
        _db_entries = sorted(self.usls.usls.find(), key=lambda e: e['_id'])
        _entries = sorted((_entry0, _entry1), key=lambda e: e['_id'])
        for e0, e1 in zip(_entries, _db_entries):
            self.assertDictEqual(e0, e1)

    def test_query(self):
        tags = lambda i: {'FR': 'testFR%d'%i, 'EN': 'testEN%d'%i}
        entries0 = [self.save_random_usl(tags=tags(i)) for i in range(10)]

        tags = lambda i: {'FR': 'test%d'%i, 'EN': 'testFR%d'%i}
        entries1 = [self.save_random_usl(tags=tags(i)) for i in range(10)]

        self.assertEqual(self.usls.query(tags={'FR': 'FR'}).count(), 10)
        self.assertEqual(self.usls.query(tags={'EN': 'FR'}).count(), 10)
        self.assertEqual(self.usls.query(tags={'EN': 'EN'}).count(), 10)
        self.assertEqual(self.usls.query(tags={'EN': 'test'}).count(), 20)
        self.assertEqual(self.usls.query(tags={'FR': 'FR', 'EN': 'test'}).count(), 10)
        self.assertEqual(self.usls.query(tags={'FR': '0', 'EN': 'FR'}).count(), 1)
        self.assertEqual(self.usls.query(tags={'FR': '0', 'EN': '1'}).count(), 0)

        self.assertEqual(self.usls.query(tags={'FR': '0', 'EN': '1'}, union=True).count(), 4)

        query_keywords = {'FR': [k['KEYWORDS']['FR'][0] for k in random.sample(entries0, 4)],
                          'EN': [k['KEYWORDS']['EN'][0] for k in entries0]}

        self.assertEqual(self.usls.query(keywords={'FR': query_keywords['FR']}).count(), 4)
        self.assertEqual(self.usls.query(keywords={'EN': query_keywords['EN']}).count(), 10)
        self.assertEqual(self.usls.query(keywords=query_keywords).count(), 4)

    def test_update_usl(self):
        entry = self.save_random_usl()

        tags = {'FR': 'test', 'EN': 'test'}
        self.usls.update(entry['_id'], tags=tags)
        self.assertEqual(self.usls.query(tags=tags).count(), 1)

        tags = {'FR': 'test', 'EN': 'popoposadopsdoapasdasderw984'}
        self.usls.update(entry['_id'], tags={'EN': tags['EN']})
        self.assertEqual(self.usls.query(tags=tags).count(), 1)

        keywords = {'FR': ['test'], 'EN': []}
        self.usls.update(entry['_id'], keywords=keywords)
        self.assertEqual(self.usls.query(keywords=keywords).count(), 1)

    def test_templates(self):
        while True:
            try:
                u = random_usl(rank_type=Text)
                paths = random.sample([p for p, t in u.paths if t.script.paradigm], 2)
                break
            except ValueError:
                continue

        self.usls.add_template(u, paths, tags_rule={l:"$0, $1" for l in TAG_LANGUAGES})
        template_entry = self.usls.get(usl=u)
        self.assertListEqual(template_entry['PARENTS'], [])
        self.assertEqual(template_entry['TEMPLATES'][0]['PATHS'], [str(p) for p in paths])
