from flask import Flask, request, jsonify
from flask_cors import CORS
from database_functions import *
import bcrypt

app=Flask(__name__)
CORS(app)

conn = get_db_connection()

@app.route("/create-account", methods=["POST"])
def register_user():
    return

@app.route("/login", methods=["GET"])
def register_user():
    return

if __name__ == "__main__":
    app.run()