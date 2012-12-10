from unittest import TestCase, main
from tranny.configuration import Configuration

class ConfigTest(TestCase):
    def test_find_sections(self):
        config = Configuration()
        config.add_section("test_1")
        config.add_section("test_2")
        config.add_section("xtest_2")
        sections = config.find_sections("test_")
        self.assertEqual(["test_1", "test_2"], sections)

if __name__ == '__main__':
    main()
