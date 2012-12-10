from os.path import exists
from os import remove
from unittest import TestCase, main
from tranny.db.pickle import PickleDB

class NetTest(TestCase):
    def setUpClass(cls):
        cls.db = PickleDB("./test.db")

    def test_add(self):
        self.db.add()


if __name__ == '__main__':
    main()
