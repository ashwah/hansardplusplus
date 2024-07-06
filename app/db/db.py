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

    def insertDocument(self, collection, document_date, document_title):
        self.connect()
        self.cur.execute("""
            INSERT INTO document (collection, document_date, document_title)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (collection, document_date, document_title))
        self.conn.commit()
        inserted_id = self.cur.fetchone()[0]
        self.close()
        return inserted_id
    
    def insertStatement(self, document_id, order_id, speaker_raw, statement_raw):
        self.connect()
        self.cur.execute("""
            INSERT INTO statement (document_id, order_id, speaker_raw, statement_raw)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (document_id, order_id, speaker_raw, statement_raw))
        self.conn.commit()
        inserted_id = self.cur.fetchone()[0]
        self.close()
        return inserted_id
    
    def insertTag(self, document_id, tag):
        self.connect()
        self.cur.execute("""
            INSERT INTO tag (document_id, tag)
            VALUES (%s, %s)
            RETURNING id;
        """, (document_id, tag))
        self.conn.commit()
        inserted_id = self.cur.fetchone()[0]
        self.close()
        return inserted_id