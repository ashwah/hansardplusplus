from db import Database

db = Database()
db.connect()

cur = db.cur

# cur.execute("""
#     CREATE TYPE collection AS ENUM ('commons', 'lords');
# """)

cur.execute("""
    CREATE TABLE IF NOT EXISTS processed (
        id SERIAL PRIMARY KEY,
        processed_date DATE,
        processed_url TEXT,
        collection collection,
        processed_state TEXT,
        processed_count INT,
        created TIMESTAMP,
        updated TIMESTAMP
    );
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS debate (
        id SERIAL PRIMARY KEY,
        processed_id INT,
        collection collection,
        debate_date DATE,
        debate_title TEXT,
        debate_url TEXT,
        debate_aggregate_url TEXT,
        debate_state TEXT,
        created TIMESTAMP,
        updated TIMESTAMP
    );
""")

cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_debate_date ON debate (debate_date);
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS statement (
        id SERIAL PRIMARY KEY,
        debate_id INT,
        order_id INT,
        speaker_raw TEXT,
        statement_raw TEXT,
        speaker_id INT
    );
""")

cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_statement_debate_id ON statement (debate_id);
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS statement_anon (
        id SERIAL PRIMARY KEY,
        debate_id INT,
        order_id INT,
        statement_raw TEXT
    );
""")

cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_statement_anon_debate_id ON statement_anon (debate_id);
""")

db.conn.commit()
db.close()