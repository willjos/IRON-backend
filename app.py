from flask import Flask, request
from flask_cors import CORS
from database_functions import *
import bcrypt

app=Flask(__name__)
CORS(app)

conn = get_db_connection()

@app.route("/create-account", methods=["POST"])
def user_create_account():
    data = request.json
    username = data['username']
    password = data['password'].encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt).decode('utf-8')
    query = "INSERT INTO users(username, hashedpw) VALUES (%s, %s)"
    parameters = (username, hashed_password)
    try:
        db_insert(query, parameters)
        return "Account Created", 200
    except:
        return "Failed to Create Account", 500

@app.route("/login", methods=["GET"])
def user_login():
    data =  request.json
    username = data['username']
    password = data['password']
    query = "SELECT hashedpw FROM users WHERE username = %s"
    parameters = (username,)    
    user_data = db_fetch(query, parameters) 
    hashed_password = user_data[0]['hashedpw']
    if(bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))):
        return "Access Granted", 200
    else:
        return "Access Denied", 403

if __name__ == "__main__":
    app.run()