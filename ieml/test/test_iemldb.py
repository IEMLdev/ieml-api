import unittest

from ieml import IEMLDatabase


class IEMLDBTest(unittest.TestCase):
    def test_change_versions(self):
        db = IEMLDatabase()
        v0 = ('master', '650f67dffc616df52d2e3440c2fc4b8cb655cf41')
        v1 = ('master', '58a3bb44f7f33752a84e0dbfdb7ebadc6a7ea8d9')
        db.set_version(*v1)
        self.assertEqual(db.get_version(), v1)

        db.set_version(*v0)
        self.assertEqual(db.get_version(), v0)



if __name__ == '__main__':
    unittest.main()
