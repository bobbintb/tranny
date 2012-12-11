datastore = None

def init_db():
    global datastore
    from tranny import config
    db_type = config.get("db", "type")
    if db_type == "pickle":
        from tranny.db.mem import MemDB
        datastore = MemDB()
    elif db_type == "pg":
        from tranny.db.pg import PgDB
        datastore = PgDB()
