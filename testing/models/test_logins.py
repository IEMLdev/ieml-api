import models.logins.logins as login
from testing.models.stub_db import ModelTestCase


class TestLogin(ModelTestCase):

    def test_create_user(self):
        login.save_user('test', 'test')
        self.assertTrue(login.is_user('test', 'test'))

    def test_user_not_found(self):
        self.assertFalse(login.is_user('test', 'test'))

    def test_invalid_password(self):
        login.save_user('test', 'test')
        self.assertFalse(login.is_user('test', 'test2'))