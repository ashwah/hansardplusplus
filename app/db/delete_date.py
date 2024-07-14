from db import Database

db = Database()
db.connect()

cur = db.cur

date = '2024-05-24'

cur.execute("""
    DELETE FROM debate WHERE debate_date = %s;
""", (date,))

cur.execute("""
    DELETE FROM statement
    WHERE debate_id IN (
        SELECT debate_id
        FROM debate
        WHERE debate_date = %s
    );
""", (date,))

cur.execute("""
    DELETE FROM statement_anon
    WHERE debate_id IN (
        SELECT debate_id
        FROM debate
        WHERE debate_date = %s
    );
""", (date,))

cur.execute("""
    DELETE FROM processed WHERE processed_date = %s;
""", (date,))

db.conn.commit()
db.close()