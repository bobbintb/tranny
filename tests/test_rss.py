from unittest import main
from tests import TrannyTestCase, get_fixture
from tranny import init_datastore, init_config
from tranny.provider.rss import RSSFeed


class RSSFeedTest(TrannyTestCase):
    def setUp(self):
        init_config(get_fixture("test_config.ini"))
        init_datastore()

    def test_get(self):
        eztv = RSSFeed(self.get_config(), "rss_eztv")
        eztv_releases = list(eztv.fetch_releases())
        self.assertFalse(eztv_releases)

        kat = RSSFeed(self.get_config(), "rss_kat")
        kat_releases = list(kat.fetch_releases())
        self.assertFalse(kat_releases)


if __name__ == '__main__':
    main()
