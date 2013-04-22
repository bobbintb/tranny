from logging import getLogger
from sqlite3 import connect
from os.path import join, dirname, abspath
from tranny import config
from tranny.db import Datastore


class SQLiteStore(Datastore):
    """
    SQLite based history storage service
    """

    def __init__(self):
        file_name = config.get_default("sqlite", "db", "history.sqlite")
        full_path = abspath(join(dirname(dirname(dirname(__file__))), file_name))
        self._db = connect(full_path)
        self.log = getLogger("db.sqlite")
        if not "history" in self._table_list():
            self._init_db()

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
        return [t[0] for t in cursor.fetchall()]

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
        with self._db:
            self._db.executescript(query)

    def add(self, release_key, section=None, source=None):
        query = """
            INSERT INTO
            history ( release_key, section, source, timestamp )
            values  (?, ?, ?, "now")
        """
        with self._db:
            self._db.execute(query, (release_key, section, source))

    def size(self):
        query = "SELECT count(*) as total FROM history"
        for row in self._db.execute(query):
            return row[0]
