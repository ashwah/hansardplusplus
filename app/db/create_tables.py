from db import Database

db = Database()
db.connect()

cur = db.cur

# cur.execute("""
#     DROP TABLE IF EXISTS document;
# """)

# cur.execute("""
#     CREATE TYPE collection AS ENUM ('commons', 'lords');
# """)

cur.execute("""
    CREATE TABLE IF NOT EXISTS debate (
        id SERIAL PRIMARY KEY,
        collection collection,
        debate_date DATE,
        debate_title TEXT    
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

cur.execute("""
    CREATE TABLE IF NOT EXISTS processed (
        id SERIAL PRIMARY KEY,
        processed_date DATE
    );
""")

# cur.execute("""
#     CREATE TABLE IF NOT EXISTS tag (
#         id SERIAL PRIMARY KEY,
#         document_id INT,
#         tag TEXT
#     );
# """)

# Insert some data into the table
# cur.execute("""
#     INSERT INTO document (collection, document_date, document_title)
#     VALUES (%s, %s, %s);
# """, ('commons', '2020-05-04', 'Covid-19_ DWP Update'))

db.conn.commit()
db.close()