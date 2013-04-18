import unittest
from tranny import util


class TestUtil(unittest.TestCase):
    def test_contains(self):
        self.assertTrue(util.contains([1, 3, 5], [1, 3, 5]))
        self.assertFalse(util.contains([1, 3, 5], [2, 4]))


if __name__ == '__main__':
    unittest.main()
