import random
import string

from ieml.usl import random_usl
from models.usls.library import usl_index
from testing.models.stub_db import ModelTestCase


def _drop_date(d):
    del d['LAST_MODIFIED']
    return d


class TestUSLsModel(ModelTestCase):

    connectors = ('library',)

    def save_random_usl(self, tags=None):
        rand_string = lambda : ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))

        _usl = random_usl()
        if not tags:
            tags = {'FR': rand_string(), 'EN': rand_string()}

        _id = self.library.save(_usl, translations=tags)

        return {
            '_id': _id,
            'USL': {
                'INDEX': usl_index(_usl),
                'IEML': str(_usl),
                'TYPE': str(_usl.ieml_object.__class__.__name__)
            },
            'TRANSLATIONS': tags,
        }

    def test_add_usl(self):
        _entry = self.save_random_usl()

        self.assertDictEqual(
            _drop_date(list(self.library.library.find())[0]),
            _entry,
            "Entry in db doesn't match.")

    def test_get_usl(self):
        _entry = self.save_random_usl()


        self.assertDictEqual(_entry, _drop_date(self.library.get(usl=_entry['USL']['IEML'])))
        self.assertDictEqual(_entry, _drop_date(self.library.get(id=_entry['_id'])))
        self.assertDictEqual(_entry, _drop_date(self.library.get(translation=_entry['TRANSLATIONS']['EN'], language='EN')))

    def test_remove_usl(self):
        _entry = self.save_random_usl()
        self.library.remove(usl=_entry['USL']['IEML'])
        self.assertEqual(self.library.library.count(), 0)

        _entry = self.save_random_usl()
        self.library.remove(id=_entry['_id'])
        self.assertEqual(self.library.library.count(), 0)

    def test_multi_add(self):
        _entry0 = self.save_random_usl()
        _entry1 = self.save_random_usl()
        _db_entries = sorted(self.library.library.find(), key=lambda e: e['_id'])
        _entries = sorted((_entry0, _entry1), key=lambda e: e['_id'])
        for e0, e1 in zip(_entries, _db_entries):
            self.assertDictEqual(e0, _drop_date(e1))

    def test_query(self):
        tags = lambda i: {'FR': 'testFR%d'%i, 'EN': 'testEN%d'%i}
        entries0 = [self.save_random_usl(tags=tags(i)) for i in range(10)]

        tags = lambda i: {'FR': 'test%d'%i, 'EN': 'testFR%d'%i}
        entries1 = [self.save_random_usl(tags=tags(i)) for i in range(10)]

        self.assertEqual(self.library.query(translations={'FR': 'FR'}).count(), 10)
        self.assertEqual(self.library.query(translations={'EN': 'FR'}).count(), 10)
        self.assertEqual(self.library.query(translations={'EN': 'EN'}).count(), 10)
        self.assertEqual(self.library.query(translations={'EN': 'test'}).count(), 20)
        self.assertEqual(self.library.query(translations={'FR': 'FR', 'EN': 'test'}).count(), 10)
        self.assertEqual(self.library.query(translations={'FR': '0', 'EN': 'FR'}).count(), 1)
        self.assertEqual(self.library.query(translations={'FR': '0', 'EN': '1'}).count(), 0)

        self.assertEqual(self.library.query(translations={'FR': '0', 'EN': '1'}, union=True).count(), 4)

    def test_update_usl(self):
        entry = self.save_random_usl()

        tags = {'FR': 'test', 'EN': 'test'}
        self.library.update(entry['_id'], translations=tags)
        self.assertEqual(self.library.query(translations=tags).count(), 1)

        tags = {'FR': 'test', 'EN': 'popoposadopsdoapasdasderw984'}
        self.library.update(entry['_id'], translations={'EN': tags['EN']})
        self.assertEqual(self.library.query(translations=tags).count(), 1)

    def test_add_notranslations(self):
        self.library.drop()
        _usl0 = random_usl()
        self.library.save(_usl0, {"FR":"", "EN": ""})
        _usl1 = random_usl()
        self.library.save(_usl1, {"FR":"", "EN": ""})

        self.assertEqual(self.library.get(usl=_usl0)['USL']['IEML'], str(_usl0))
        self.assertEqual(self.library.get(usl=_usl1)['USL']['IEML'], str(_usl1))

    def test_indexes(self):
        _usl0 = random_usl()
        self.library.save(_usl0, {"FR": "", "EN": ""})
        with self.assertRaises(ValueError):
            self.library.save(_usl0, _usl0.auto_translation())



    # def test_templates(self):
    #     while True:
    #         try:
    #             u = random_usl(rank_type=Text)
    #             paths = random.sample([p for p, t in u.paths.items() if t.script.paradigm], 2)
    #             break
    #         except ValueError:
    #             continue
    #
    #     self.library.add_template(u, paths, tags_rule={l:"$0, $1" for l in TAG_LANGUAGES})
    #     template_entry = self.library.get(usl=u)
    #     self.assertListEqual(template_entry['PARENTS'], [])
    #     self.assertEqual(template_entry['TEMPLATES'][0]['PATHS'], [str(p) for p in paths])
