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
    data = request.json
    username = data['username']
    password = data['password']
    query = "SELECT hashedpw FROM users WHERE username = %s"
    parameters = (username,)    
    user_data = db_fetch(query, parameters) # do we need a try except here?
    hashed_password = user_data[0]['hashedpw']
    if(bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))):
        return "Access Granted", 200
    else:
        return "Access Denied", 403

@app.route("/add-workout", methods=["POST"])
def add_workout():
    data = request.json
    username = data['username']
    workout_name = data['workout_name']
    exercises = data['exercises']
    query_workouts = """
            INSERT INTO user_workouts(user_id, workout_name)
            VALUES ((SELECT id FROM users WHERE username = %s), %s)
            ON CONFLICT DO NOTHING;
        """
    parameters_workouts = (username, workout_name)
    try:
        db_insert(query_workouts, parameters_workouts)
        for exercise in exercises:
            query_exercise = """
                INSERT INTO user_exercises(user_id, exercise_name)
                VALUES ((SELECT id FROM users WHERE username = %s), %s)
                ON CONFLICT DO NOTHING;
            """
            parameters_exercise = (username, exercise)
            query_workout_exercises = """
                INSERT INTO workout_exercises(user_id, exercise_id, workout_id)
                VALUES (
                    (SELECT id FROM users WHERE username = %s), 
                    (SELECT id FROM user_exercises 
                        WHERE user_id=(SELECT id FROM users WHERE username = %s) AND exercise_name=%s), 
                    (SELECT id FROM user_workouts 
                        WHERE user_id=(SELECT id FROM users WHERE username = %s) AND workout_name=%s)
                );
            """
            parameters_workout_exercises = (username, username, exercise, username, workout_name)
            db_insert(query_exercise, parameters_exercise)
            db_insert(query_workout_exercises, parameters_workout_exercises)
        return "Workout Added", 200
    except:
        return "Failed to Add Workout", 500

@app.route("/add-exercise", methods=["POST"])
def add_exercise():
    data = request.json
    username = data['username']
    exercise_name = data['exercise_name']
    query = """
            INSERT INTO user_exercises(user_id, exercise_name)
            VALUES ((SELECT id FROM users WHERE username = %s), %s);
            """
    parameters = (username, exercise_name)
    try:
        db_insert(query, parameters)
        return "Exercise Added", 200
    except:
        return "Failed to Add Exercise", 500

if __name__ == "__main__":
    app.run()