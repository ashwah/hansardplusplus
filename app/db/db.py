import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from.env file
load_dotenv()

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.port = int(os.getenv('DB_PORT'))
        self.username = os.getenv('DB_USERNAME')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_DATABASE')
        self.conn = None
        self.cur = None

    def connect(self):
        self.conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            dbname=self.database
        )
        self.cur = self.conn.cursor()

    def close(self):
        self.cur.close()
        self.conn.close()

    def insertDebate(self, collection, debate_date, debate_title):
        self.connect()
        self.cur.execute("""
            INSERT INTO debate (collection, debate_date, debate_title)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (collection, debate_date, debate_title))
        self.conn.commit()
        inserted_id = self.cur.fetchone()[0]
        self.close()
        return inserted_id
    
    def insertStatement(self, debate_id, order_id, speaker_raw, statement_raw, speaker_id):
        self.connect()
        self.cur.execute("""
            INSERT INTO statement (debate_id, order_id, speaker_raw, statement_raw, speaker_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (debate_id, order_id, speaker_raw, statement_raw, speaker_id))
        self.conn.commit()
        inserted_id = self.cur.fetchone()[0]
        self.close()
        return inserted_id
    
    def insertStatementAnon(self, debate_id, order_id, statement_raw):
        self.connect()
        self.cur.execute("""
            INSERT INTO statement_anon (debate_id, order_id, statement_raw)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (debate_id, order_id, statement_raw))
        self.conn.commit()
        inserted_id = self.cur.fetchone()[0]
        self.close()
        return inserted_id

    def insertProcessedDate(self, processed_date):
        self.connect()
        self.cur.execute("""
            INSERT INTO processed (processed_date)
            VALUES (%s)
            RETURNING id;
        """, (processed_date,))
        self.conn.commit()
        inserted_id = self.cur.fetchone()[0]
        self.close()
        return inserted_id    
        
    def getProcessedDates(self):
        self.connect()
        self.cur.execute("""
            SELECT processed_date
            FROM processed;
        """)
        dates = [row[0] for row in self.cur.fetchall()]
        self.close()
        return dates

    # def insertTag(self, document_id, tag):
    #     self.connect()
    #     self.cur.execute("""
    #         INSERT INTO tag (document_id, tag)
    #         VALUES (%s, %s)
    #         RETURNING id;
    #     """, (document_id, tag))
    #     self.conn.commit()
    #     inserted_id = self.cur.fetchone()[0]
    #     self.close()
    #     return inserted_id