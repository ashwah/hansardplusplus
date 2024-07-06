from db import Database

db = Database()
db.connect()

cur = db.cur

cur.execute("""
    TRUNCATE TABLE document;
""")

cur.execute("""
    TRUNCATE TABLE statement;
""")

cur.execute("""
    TRUNCATE TABLE tag;
""")

db.conn.commit()
db.close()