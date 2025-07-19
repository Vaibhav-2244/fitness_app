from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

# --------------------------
# User Signup
# --------------------------
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data['username']
    email = data['email']
    password = generate_password_hash(data['password'])

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", (username, email, password))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'User created successfully'})

# --------------------------
# User Login
# --------------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE email = %s", (email,))
    result = cur.fetchone()
    cur.close()

    if result and check_password_hash(result[1], password):
        return jsonify({'message': 'Login successful', 'user_id': result[0]})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# --------------------------
# Log Workout
# --------------------------
@app.route('/log_workout', methods=['POST'])
def log_workout():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO workouts (user_id, activity_type, duration_minutes, distance_km, calories_burned, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data['user_id'], data['activity_type'], data['duration_minutes'], data.get('distance_km', 0),
        data.get('calories_burned', 0), data.get('start_time'), data.get('end_time')
    ))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Workout logged successfully'})

# --------------------------
# Log GPS Route
# --------------------------
@app.route('/log_gps', methods=['POST'])
def log_gps():
    data = request.json
    cur = mysql.connection.cursor()
    for point in data['coordinates']:
        cur.execute("""
            INSERT INTO gps_routes (workout_id, latitude, longitude, timestamp)
            VALUES (%s, %s, %s, %s)
        """, (data['workout_id'], point['lat'], point['lng'], point['timestamp']))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'GPS route saved'})

# --------------------------
# Log Meal
# --------------------------
@app.route('/log_meal', methods=['POST'])
def log_meal():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO meals (user_id, meal_type, description, calories, meal_time)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        data['user_id'], data['meal_type'], data['description'], data['calories'], data['meal_time']
    ))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Meal logged'})

# --------------------------
# Log Water Intake
# --------------------------
@app.route('/log_water', methods=['POST'])
def log_water():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO water_intake (user_id, amount_ml, intake_time)
        VALUES (%s, %s, %s)
    """, (
        data['user_id'], data['amount_ml'], data['intake_time']
    ))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Water intake logged'})

# --------------------------
# Set Goal
# --------------------------
@app.route('/set_goal', methods=['POST'])
def set_goal():
    data = request.json
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO fitness_goals (user_id, goal_type, target_value, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        data['user_id'], data['goal_type'], data['target_value'], data['start_date'], data['end_date']
    ))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Goal set successfully'})

# --------------------------
# Get Progress
# --------------------------
@app.route('/progress/<int:user_id>', methods=['GET'])
def progress(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM workouts WHERE user_id = %s", (user_id,))
    workouts = cur.fetchall()
    cur.execute("SELECT * FROM meals WHERE user_id = %s", (user_id,))
    meals = cur.fetchall()
    cur.execute("SELECT * FROM water_intake WHERE user_id = %s", (user_id,))
    water = cur.fetchall()
    cur.close()

    return jsonify({
        'workouts': workouts,
        'meals': meals,
        'water': water
    })

# --------------------------
# Root API for health check
# --------------------------
@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Fitness Tracker API running!'})

if __name__ == '__main__':
    app.run(debug=True)
