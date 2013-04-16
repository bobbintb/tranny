from os.path import exists
from os import remove
from unittest import TestCase, main
from tranny.db.gherkin import GherkinStore


class NetTest(TestCase):
    def setUpClass(cls):
        cls.db = GherkinStore("./test.db")

    def test_add(self):
        self.db.add()


if __name__ == '__main__':
    main()
