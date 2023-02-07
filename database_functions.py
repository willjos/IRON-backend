import psycopg2
import psycopg2.extras as pse
import os
from dotenv import load_dotenv

# load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(f"dbname=culqcxrn user=culqcxrn password={os.getenv('DB_PASSWORD')} host=manny.db.elephantsql.com port=5432")
        return conn
    except:
        print('Error Connecting to Database')

conn = get_db_connection()

def db_insert(query, parameters):
    if conn != None:
        with conn.cursor(cursor_factory = pse.RealDictCursor) as cur:
            cur.execute(query, parameters)
            conn.commit()
    else:
        return "No connection"

def db_fetch(query, parameters):
    if conn != None:
        with conn.cursor(cursor_factory=pse.RealDictCursor) as cur:
            cur.execute(query, parameters)
            fetched_data = cur.fetchall()
            return fetched_data
    else:
        return "No connection"

def db_insert_fetch(query, parameters):
    if conn != None:
        with conn.cursor(cursor_factory = pse.RealDictCursor) as cur:
            cur.execute(query, parameters)
            fetched_data = cur.fetchall()
            conn.commit()
            return fetched_data
    else:
        return "No connection"