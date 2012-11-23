from unittest import TestCase, main
from tranny.rss import RSSFeed

class RSSFeedTest(TestCase):
    def test_get(self):
        feed = RSSFeed("http://www.dailytvtorrents.org/rss/show/glee", "test_feed")
        self.assertTrue(feed.update())

if __name__ == '__main__':
    main()
