from db import Database

db = Database()
db.connect()

cur = db.cur

cur.execute("""
    TRUNCATE TABLE debate;
""")

cur.execute("""
    ALTER SEQUENCE debate_id_seq RESTART WITH 1;
""")

cur.execute("""
    TRUNCATE TABLE statement;
""")

cur.execute("""
    ALTER SEQUENCE statement_id_seq RESTART WITH 1;
""")

cur.execute("""
    TRUNCATE TABLE statement_anon;
""")

cur.execute("""
    ALTER SEQUENCE statement_anon_id_seq RESTART WITH 1;
""")

cur.execute("""
    TRUNCATE TABLE processed;
""")

cur.execute("""
    ALTER SEQUENCE processed_id_seq RESTART WITH 1;
""")

# cur.execute("""
#     TRUNCATE TABLE tag;
# """)

# cur.execute("""
#     ALTER SEQUENCE tag_id_seq RESTART WITH 1;
# """)

db.conn.commit()
db.close()