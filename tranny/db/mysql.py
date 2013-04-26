from logging import getLogger
from oursql import connect
from tranny.db.sqlite import SQLiteStore


class MySQLStore(SQLiteStore):
    """
    SQLite based history storage service
    """
    _section_name = "mysql"

    def _connect(self):
        if not self._db:
            db_name = self.config.get_default(self._section_name, "db", "localhost")
            host = self.config.get_default(self._section_name, "host", "localhost")
            port = self.config.get_default(self._section_name, "port", 3306, int)
            user = self.config.get_default(self._section_name, "user", None)
            password = self.config.get_default(self._section_name, "password", None)
            self._db = connect(host=host, user=user, passwd=password, port=port, db=db_name)

    def _table_list(self):
        """ Fetch a list of tables currently in the database

        :return: List of table names
        :rtype: str[]
        """
        cursor = self._db.cursor()
        cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES")
        results = cursor.fetchall()
        return [t[0] for t in results]

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
            values  (?, ?, ?, now())
        """
        with self._db as cur:
            cur.execute(query, (release_key, section, source))
