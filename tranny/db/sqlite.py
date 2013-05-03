from logging import getLogger
from sqlite3 import connect
from os.path import join, dirname, abspath
from tranny import config
from tranny.db import Datastore


class SQLiteStore(Datastore):
    """
    SQLite based datastore service
    """

    def __init__(self, config=None):
        self.config = config
        self.log = getLogger("db.sqlite")
        self._connect()
        if not "history" in self._table_list():
            self._init_db()

    def _connect(self):
        """ Connect to the database file which

        :return:
        :rtype:
        """
        file_name = config.get_default("sqlite", "db", "history.sqlite")
        full_path = abspath(join(dirname(dirname(dirname(__file__))), file_name))
        self._db = connect(full_path)

        # Make sure we return dict's for each row, sqlite doesnt have a built in for this
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        # noinspection PyPropertyAccess
        self._db.row_factory = dict_factory

    def __contains__(self, release_key):
        """ Provides support for the in keyword:

        if key in datastore_instance:
            blah()


        :param release_key:
        :type release_key:
        :return: Key exists in db status
        :rtype: bool
        """
        cur = self._db.cursor()
        cur.execute("SELECT release_key FROM history WHERE release_key = ?", (release_key,))
        result = cur.fetchone()
        return bool(result)

    def _table_list(self):
        """ Fetch a list of tables currently in the database

        :return: List of table names
        :rtype: str[]
        """
        cursor = self._db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [t['name'] for t in cursor.fetchall()]

    def _init_db(self):
        """ Create the default table schemas """
        query = """
            CREATE TABLE "history" (
                "release_key"  TEXT NOT NULL,
                "section"  TEXT,
                "source"  TEXT,
                "timestamp"  datetime NOT NULL,
                PRIMARY KEY ("release_key" ASC)
            );
        """
        with self._db as cur:
            cur.execute(query)

    def add(self, release_key, section=None, source=None):
        query = """
            INSERT INTO
            history ( release_key, section, source, timestamp )
            values  (?, ?, ?, "now")
        """
        with self._db as cur:
            cur.execute(query, (release_key, section, source))

    def size(self):
        query = "SELECT count(*) as total FROM history"
        with self._db as cur:
            for row in cur.execute(query):
                return row['total']

    def fetch_newest(self, limit=25):
        assert limit >= 1, "Invalid limit value, must be positive integer"
        query = """
            SELECT
                release_key, section, source, timestamp
            FROM
                history
            ORDER BY
                timestamp DESC
            LIMIT 0, ?
        """
        cur = self._db.cursor()
        cur.execute(query, (limit,))
        results = cur.fetchall()
        return results
