import random
import string
import unittest

from _pytest.unittest import UnitTestCase
from handlers import save_usl, get_usl
from handlers.usl.usl import delete_usl
from ieml.usl.tools import random_usl
from testing.models.stub_db import modelTestCase

rand_string = lambda: ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))

class TestUslHandler(modelTestCase('usl')):
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

    def _save_usl(self):
        _usl = random_usl()
        tags = {'f'}
        fr = rand_string()
        en = rand_string()
        self._assert_success(save_usl({
            'ieml': str(_usl),
            'fr': fr,
            'en': en
        }))
        return {'ieml': str(_usl),
                'tags': {'FR': fr, 'EN': en},
                'keywords': {'FR': [], 'EN': []}}


    def test_save_usl(self):
        entry = self._save_usl()
        self.assertDictEqual(self._assert_success(get_usl({'ieml': str(entry['ieml'])})),
                         {'success': True, **entry})

    def test_delete_usl(self):
        entry = self._save_usl()
        self._assert_success(delete_usl({'ieml': str(entry['ieml'])}))

        self._assert_fail(get_usl({'ieml': str(entry['ieml'])}))