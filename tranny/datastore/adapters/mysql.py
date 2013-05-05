from logging import getLogger
from oursql import connect, DictCursor
from tranny.datastore.adapters.sqlite import SQLiteStore


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
            self._db = connect(
                host=host,
                user=user,
                passwd=password,
                port=port,
                db=db_name,
                autoping=True,
                default_cursor=DictCursor
            )

    def _table_list(self):
        """ Fetch a list of tables currently in the database

        :return: List of table names
        :rtype: str[]
        """
        cursor = self._db.cursor()
        cursor.execute("""SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'history'""")
        results = cursor.fetchall()
        return [t['TABLE_NAME'] for t in results]

    def _init_db(self):
        """ Create the default table schemas """
        query = """
            CREATE TABLE history.`history` (
                `release_key` varchar(255) NOT NULL ,
                `section` varchar(255) NOT NULL ,
                `release_name` varchar(255) NOT NULL ,
                `source` varchar(255) NOT NULL ,
                `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP ,
                UNIQUE INDEX `release_idx` (`release_key`)
            )
        """
        with self._db as cur:
            cur.execute(query)

    def add(self, release_key, release_name, section=None, source=None):
        query = """
            INSERT INTO
            history ( release_key, release_name, section, source, timestamp )
            values  (?, ?, ?, ?, now())
        """
        with self._db as cur:
            cur.execute(query, (release_key, release_name, section, source))

    def fetch(self, limit=25):
        query = """
            SELECT
                release_key, section, release_name, source, timestamp
            FROM
                history
            ORDER BY
                timestamp DESC
        """
        if limit:
            query += """ LIMIT 0, ?"""
            args = (limit,)
        else:
            args = ()
        cur = self._db.cursor()
        cur.execute(query, args)
        results = cur.fetchall()
        return results
