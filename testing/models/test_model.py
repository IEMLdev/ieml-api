from testing.models.stub_db import ModelTestCase, _tag, paradigms
from models.exceptions import RootParadigmMissing, RootParadigmIntersection, InvalidTags, DuplicateTag
from ieml.script.operator import sc


class TestModel(ModelTestCase):
    def test_insert_term(self):
        script = sc("M:M:M:.U:U:U:.e.-")
        self.terms.add_term(script, {'FR': 'fr', 'EN': 'en'}, [], root=True)
        self.assertTrue(self.terms.get_term(str(script))['_id'] == "M:M:M:.U:U:U:.e.-")
        self.terms.remove_term(script)

    def test_insert_multiple_term(self):
        root = sc('O:M:M:.')
        self.terms.add_term(root, {'FR': 'fr', 'EN': 'en'}, [], root=True)
        for i, s in enumerate(root.singular_sequences):
            self.terms.add_term(s, {'FR': 'fr'+str(i), 'EN': 'en'+str(i)}, [])
        p = sc('O:M:S:.')
        self.terms.add_term(p, {'FR': 'frp', 'EN': 'enp'}, [])

        self.terms.remove_term(p)
        for s in root.singular_sequences:
            self.terms.remove_term(s)
        self.terms.remove_term(root)

        self.assertEqual(list(self.terms.get_all_terms()), [])

    def test_fail_no_root(self):
        s = sc('A:')
        try:
            self.terms.add_term(s, {'FR': 'fr', 'EN': 'en'}, [])
        except Exception:
            self.assertRaises(RootParadigmMissing)

    def test_fail_paradigm_intersect(self):
        s1 = sc('M:')
        s2 = sc('F:')
        self.terms.add_term(s1, _tag(), [], root=True)
        with self.assertRaises(RootParadigmIntersection):
            self.terms.add_term(s2, _tag(), [], root=True)

    def test_update(self):
        s1 = sc('F:')
        self.terms.add_term(s1, {'FR': 'fr', 'EN': 'en'}, [], root=True)
        newt = {'FR': 'fr2', 'EN': 'en2'}
        self.terms.update_term(s1, tags=newt)
        self.assertEqual(self.terms.get_term(s1)['TAGS'], newt)
        self.terms.remove_term(s1)

    def test_remove_root_paradigm(self):
        paradigm = paradigms[0]
        self._save_paradigm(paradigm)

        self.terms.remove_term(paradigm.root, remove_roots_child=True)
        self.assertTrue(self.terms.get_all_terms().count() == 0,
                        msg='Delete of root paradigm have not remove subsequent paradigms.')

    def test_tag(self):
        with self.assertRaises(InvalidTags, msg='Term saved with an empty tag.') as e:
            self.terms.add_term(sc('M:'), tags={}, root=True, inhibits=[])

        self.assertTrue(self._count() == 0, msg='Term created anyway.')

        with self.assertRaises(InvalidTags, msg='Term saved with missing languages.'):
            self.terms.add_term(sc('M:'), tags={'FR':'fdsas'}, root=True, inhibits=[])
        self.assertTrue(self._count() == 0, msg='Term created anyway.')

        with self.assertRaises(InvalidTags, msg='Term saved with an unknown language.'):
            self.terms.add_term(sc('M:'), tags={'QW': 'dsadsa'}, root=True, inhibits=[])
        self.assertTrue(self._count() == 0, msg='Term created anyway.')

        with self.assertRaises(InvalidTags, msg='Term saved with tag of incompatible type.'):
            self.terms.add_term(sc('M:'), tags={
                'FR': ('f', 'e', 'e'),
                'EN': ()
            }, root=True, inhibits=[])
        self.assertTrue(self._count() == 0, msg='Term created anyway.')

        tag = _tag()

        self.terms.add_term(sc('M:'), tags=tag, root=True, inhibits=[])

        with self.assertRaises(DuplicateTag, msg='Term saved with duplicate tag.'):
            self.terms.add_term(sc('O:'), tags=tag, root=True, inhibits=[])

        self._clear()

    def test_search_by_tag(self):
        tag = _tag()
        self.terms.add_term(sc('M:'), tag, [], root=True)
        self.assertTrue(self.terms.search_by_tag(tag['EN'], 'EN').count() == 1)

    def test_rank(self):
        paradigm = paradigms[0]
        self._save_paradigm(paradigm)
