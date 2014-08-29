from unittest import main
from testcase import TrannyTestCase
from tranny.provider.rss import RSSFeed


class RSSFeedTest(TrannyTestCase):

    def test_get(self):
        eztv = RSSFeed("rss_eztv")
        eztv_releases = list(eztv.fetch_releases())
        self.assertFalse(eztv_releases)

        kat = RSSFeed(self.get_config(), "rss_kat")
        kat_releases = list(kat.fetch_releases())
        self.assertFalse(kat_releases)


if __name__ == '__main__':
    main()
