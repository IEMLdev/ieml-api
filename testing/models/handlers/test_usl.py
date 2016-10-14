import random
import string
import unittest

import handlers as h
from ieml.usl.tools import random_usl
from testing.models.stub_db import ModelTestCase


def rand_string():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))


class TestUslHandler(ModelTestCase):
    connectors = ('usls',)

    def _assert_success(self, m):
        if not isinstance(m, dict) or 'success' not in m:
            self.fail("Responses malformed.")

        if not m['success']:
            self.fail("Request response is not successful : %s"%m['message'])
        return m

    def _assert_fail(self, m):
        if not isinstance(m, dict) or 'success' not in m:
            self.fail("Responses malformed.")

        if not m['success']:
            return m

        self.fail("Request is successful, should have failed.")

    def _save_usl(self, fr=None, en=None):
        _usl = random_usl()
        if not fr:
            fr = rand_string()
        if not en:
            en = rand_string()

        self._assert_success(h.save_usl({
            'ieml': str(_usl),
            'fr': fr,
            'en': en
        }))
        return {'ieml': str(_usl),
                'tags': {'FR': fr, 'EN': en},
                'keywords': {'FR': [], 'EN': []}}

    def test_save_usl(self):
        entry = self._save_usl()
        self.assertDictEqual(self._assert_success(h.get_usl({'ieml': str(entry['ieml'])})),
                         {'success': True, **entry})

    def test_delete_usl(self):
        entry = self._save_usl()
        self._assert_success(h.delete_usl({'ieml': str(entry['ieml'])}))

        self._assert_fail(h.get_usl({'ieml': str(entry['ieml'])}))

    def test_update_usl(self):
        entry = self._save_usl()
        self._assert_success(h.update_usl({'ieml': str(entry['ieml']), 'fr': 'test', 'en': 'test'}))

        e = self._assert_success(h.query_usl({'fr': 'test'}))
        self.assertEqual(len(e['match']), 1)
        self.assertEqual(e['match'][0]['ieml'], str(entry['ieml']))

        e = self._assert_success(h.query_usl({'en': 'test'}))
        self.assertEqual(len(e['match']), 1)
        self.assertEqual(e['match'][0]['ieml'], str(entry['ieml']))

    def test_query(self):
        entry = self._save_usl(fr='query')
        res = self._assert_success(h.query_usl({'fr': 'query'}))
        self.assertEqual(len(res['match']), 1)
        self.assertEqual(res['match'][0]['ieml'], str(entry['ieml']))
