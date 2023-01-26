import psycopg2
import psycopg2.extras as pse
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import bcrypt
from dotenv import load_dotenv

load_dotenv()

app=Flask(__name__)
CORS(app)

def get_db_connection():
    try:
        conn = psycopg2.connect(f"dbname=culqcxrn user=culqcxrn password={os.getenv('DB_PASSWORD')} host=manny.db.elephantsql.com port=5432")
        return conn
    except:
        print('Error Connecting to Database')

conn = get_db_connection()

if __name__ == "__main__":
    app.run()