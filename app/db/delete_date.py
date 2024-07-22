from db import Database

db = Database()
db.connect()

cur = db.cur

date = '2024-01-31'
collection = 'lords'

cur.execute("""
    DELETE FROM debate 
    WHERE debate_date = %s
    AND collection = %s;
""", (date, collection))

cur.execute("""
    DELETE FROM statement
    WHERE debate_id IN (
        SELECT debate_id
        FROM debate
        WHERE debate_date = %s
        AND collection = %s
    );
""", (date, collection))

cur.execute("""
    DELETE FROM statement_anon
    WHERE debate_id IN (
        SELECT debate_id
        FROM debate
        WHERE debate_date = %s
        AND collection = %s
    );
""", (date, collection))

cur.execute("""
    DELETE FROM processed ç
    WHERE processed_date = %s
    AND collection = %s;
""", (date, collection))

db.conn.commit()
db.close()