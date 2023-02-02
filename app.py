from flask import Flask, request
from flask_cors import CORS
from database_functions import *
import bcrypt

app=Flask(__name__)
CORS(app)

conn = get_db_connection()

@app.route('/', methods=['GET'])
def homepage():
    return "IRON backend server"

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

@app.route("/login", methods=["POST"])
def user_login():
    data = request.json
    username = data['username']
    password = data['password']
    query = "SELECT hashedpw FROM users WHERE username = %s"
    parameters = (username,)
    try:    
        user_data = db_fetch(query, parameters)
        hashed_password = user_data[0]['hashedpw']
        if(bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))):
            return "Access Granted", 200
    except:
        return "Access Denied", 403

@app.route("/add-workout", methods=["POST"])
def add_workout():
    data = request.json
    username = data['username']
    workout_name = data['workout_name']
    exercises = data['exercises']
    query_workouts = """
        INSERT INTO user_workouts(user_id, workout_name)
        VALUES ((SELECT user_id FROM users WHERE username = %s), %s)
        ON CONFLICT DO NOTHING;
    """
    parameters_workouts = (username, workout_name)
    try:
        db_insert(query_workouts, parameters_workouts)
        for exercise in exercises:
            query_exercise = """
                INSERT INTO user_exercises(user_id, exercise_name)
                VALUES ((SELECT user_id FROM users WHERE username = %s), %s)
                ON CONFLICT DO NOTHING;
            """
            parameters_exercise = (username, exercise)
            query_workout_exercises = """
                INSERT INTO workout_exercises(exercise_id, workout_id)
                VALUES (
                    (SELECT exercise_id FROM user_exercises 
                        WHERE user_id=(SELECT user_id FROM users WHERE username = %s) AND exercise_name=%s), 
                    (SELECT workout_id FROM user_workouts 
                        WHERE user_id=(SELECT user_id FROM users WHERE username = %s) AND workout_name=%s)
                );
            """
            parameters_workout_exercises = (username, exercise, username, workout_name)
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
        VALUES ((SELECT user_id FROM users WHERE username = %s), %s);
    """
    parameters = (username, exercise_name)
    try:
        db_insert(query, parameters)
        return "Exercise Added", 200
    except:
        return "Failed to Add Exercise", 500

@app.route("/log-workout", methods=["POST"])
def log_workout():
    data = request.json
    username = data['username']
    workout_data = data['workout_data']
    workout_name = workout_data['name']
    exercise_data = workout_data['exercises']
    query_workout_log = """
        INSERT INTO workout_logs(workout_id, logged_at)
        VALUES (
            (SELECT workout_id from user_workouts 
                WHERE user_id=(SELECT user_id FROM users WHERE username = %s) AND workout_name=%s), 
            current_timestamp
        )
        RETURNING workout_log_id;
    """
    parameters_workout_log = (username, workout_name)
    try:
        workout_log_fetch = db_insert_fetch(query_workout_log, parameters_workout_log)
        workout_log_id = workout_log_fetch[0]['workout_log_id']
        print(workout_log_id)
        for exercise in exercise_data:
            for set in exercise['sets']:
                query_set_log = """
                    INSERT INTO set_logs(workout_exercise_id, workout_log_id, weight, reps)
                    VALUES (
                        (SELECT workout_exercise_id FROM workout_exercises 
                        WHERE exercise_id=(SELECT exercise_id from user_exercises 
                            WHERE user_id=(SELECT user_id from users WHERE username=%s)
                            AND exercise_name=%s)
                        AND workout_id=(SELECT workout_id FROM user_workouts 
                            WHERE user_id=(SELECT user_id from users WHERE username=%s)
                            AND workout_name=%s)), 
                        %s, %s, %s)
                """
                parameters_set_log = (username, exercise['name'], username, workout_name, workout_log_id, set['weight'], set['reps'])
                db_insert(query_set_log, parameters_set_log)
                print('set logged', exercise['name'])
        return 'Workout Logged', 200
    except:
        return 'Failed to Log Workout', 500

@app.route("/get-workouts", methods=["GET"])
def get_workouts():
    username = request.args['username']
    query = """
        SELECT 
        user_workouts.*,
        workout_exercises.workout_exercise_id,
        user_exercises.exercise_id,
        user_exercises.exercise_name
            FROM user_workouts 
            JOIN workout_exercises 
                ON user_workouts.workout_id = workout_exercises.workout_id
                JOIN user_exercises 
                    ON workout_exercises.exercise_id = user_exercises.exercise_id 
                        WHERE user_exercises.user_id = (SELECT user_id FROM users WHERE username = %s);
    """
    parameters = (username, )
    try:
        user_workout_data = db_fetch(query, parameters)
        return user_workout_data, 200
    except:
        return 'Failed to Get Workouts', 500

@app.route("/get-exercises", methods=["GET"]) # not sure this is necessary considering above endpoint gives all info.
def get_exercises():
    username = request.args['username']
    query = """
        SELECT * FROM user_exercises 
        WHERE user_id = (SELECT user_id FROM users WHERE username = %s);
    """
    parameters = (username, )
    user_exercise_data = db_fetch(query, parameters)
    return user_exercise_data, 200

if __name__ == "__main__":
    app.run(debug=True)