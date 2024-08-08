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

    def insertProcessed(self, processed_date, processed_url, collection, processed_state, processed_count, created, updated):
        self.connect()
        self.cur.execute("""
            INSERT INTO processed (processed_date, processed_url, collection, processed_state, processed_count, created, updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (processed_date, processed_url, collection, processed_state, processed_count, created, updated))
        self.conn.commit()
        inserted_id = self.cur.fetchone()[0]
        self.close()
        return inserted_id    

    def updateProcessed(self, id, processed_date=None, processed_url=None, collection=None, processed_state=None, processed_count=None, created=None, updated=None):
        self.connect()
        update_fields = []
        update_values = []
        
        if processed_date:
            update_fields.append("processed_date = %s")
            update_values.append(processed_date)
        if processed_url:
            update_fields.append("processed_url = %s")
            update_values.append(processed_url)
        if collection:
            update_fields.append("collection = %s")
            update_values.append(collection)
        if processed_state:
            update_fields.append("processed_state = %s")
            update_values.append(processed_state)
        if processed_count:
            update_fields.append("processed_count = %s")
            update_values.append(processed_count)
        if created:
            update_fields.append("created = %s")
            update_values.append(created)
        if updated:
            update_fields.append("updated = %s")
            update_values.append(updated)
        
        update_values.append(id)
        
        self.cur.execute("""
            UPDATE processed
            SET {}
            WHERE id = %s;
        """.format(", ".join(update_fields)), update_values)
        self.conn.commit()
        self.close()
        
    def getProcessedDateList(self, collection):
        self.connect()
        self.cur.execute("""
            SELECT processed_date
            FROM processed
            WHERE collection = %s AND processed_state != 'unready';
        """, (collection,))
        dates = [row[0] for row in self.cur.fetchall()]
        self.close()
        return dates
    
    def getProcessedDate(self, collection, date):
        self.connect()
        self.cur.execute("""
            SELECT id
            FROM processed
            WHERE collection = %s AND processed_date = %s;
        """, (collection, date))
        row = self.cur.fetchone()
        if row:
            id = row[0]
        else:
            id = None
        self.close()
        return id

    def getDebatesWithMatchingTitle(self, collection, date, title):
        self.connect()
        self.cur.execute("""
            SELECT id
            FROM debate
            WHERE collection = %s AND debate_date = %s AND debate_title = %s AND debate_state = 'pending';
        """, (collection, date, title))
        ids = [row[0] for row in self.cur.fetchall()]
        self.close()
        return ids

    def getDebateFromId(self, debate_id):
        self.connect()
        self.cur.execute("""
            SELECT *
            FROM debate
            WHERE id = %s;
        """, (debate_id,))
        return self.cur.fetchall()[0]

    def getStatementsFromDebate(self, debate_id):
        self.connect()
        self.cur.execute("""
            SELECT order_id, speaker_raw, statement_raw
            FROM statement
            WHERE debate_id = %s;
        """, (debate_id,))
        return self.cur.fetchall()

    def getStatementsAnonFromDebate(self, debate_id):
        self.connect()
        self.cur.execute("""
            SELECT order_id, statement_raw
            FROM statement_anon
            WHERE debate_id = %s;
        """, (debate_id,))
        return self.cur.fetchall()
    
    def insertDebate(self, processed_id, collection, debate_date, debate_title, debate_url, debate_aggregate_url, debate_state, created, updated):
        self.connect()
        self.cur.execute("""
            INSERT INTO debate (processed_id, collection, debate_date, debate_title, debate_url, debate_aggregate_url, debate_state, created, updated)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (processed_id, collection, debate_date, debate_title, debate_url, debate_aggregate_url, debate_state, created, updated))
        self.conn.commit()
        inserted_id = self.cur.fetchone()[0]
        self.close()
        return inserted_id
    
    def updateDebate(self, id, processed_id=None, collection=None, debate_date=None, debate_title=None, debate_url=None, debate_aggregate_url=None, debate_state=None, created=None, updated=None):
        self.connect()
        update_fields = []
        update_values = []

        if processed_id:
            update_fields.append("processed_id = %s")
            update_values.append(processed_id)        
        if collection:
            update_fields.append("collection = %s")
            update_values.append(collection)
        if debate_date:
            update_fields.append("debate_date = %s")
            update_values.append(debate_date)
        if collection:
            update_fields.append("collection = %s")
            update_values.append(collection)
        if debate_title:
            update_fields.append("debate_title = %s")
            update_values.append(debate_title)
        if debate_url:
            update_fields.append("debate_url = %s")
            update_values.append(debate_url)
        if debate_aggregate_url:
            update_fields.append("debate_aggregate_url = %s")
            update_values.append(debate_aggregate_url)
        if debate_state:
            update_fields.append("debate_state = %s")
            update_values.append(debate_state)
        if created:
            update_fields.append("created = %s")
            update_values.append(created)
        if updated:
            update_fields.append("updated = %s")
            update_values.append(updated)
        
        update_values.append(id)
        
        self.cur.execute("""
            UPDATE debate
            SET {}
            WHERE id = %s;
        """.format(", ".join(update_fields)), update_values)
        self.conn.commit()
        self.close()

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
