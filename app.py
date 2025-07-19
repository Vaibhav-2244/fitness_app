from flask import Flask, request, jsonify
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc
import datetime

app = Flask(__name__)

# Connect to Azure SQL
def get_db_connection():
    return pyodbc.connect(Config.CONNECTION_STRING)

# --------------------------
# Signup
# --------------------------
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data['username']
    email = data['email']
    password = generate_password_hash(data['password'])

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
    """, (username, email, password))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'User created successfully'})


# --------------------------
# Login
# --------------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row and check_password_hash(row.password_hash, password):
        return jsonify({'message': 'Login successful', 'user_id': row.id})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


# --------------------------
# Log Workout (POST)
# --------------------------
@app.route('/workouts', methods=['POST'])
def log_workout():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO workouts (user_id, activity_type, duration_minutes, distance_km, calories_burned, start_time, end_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data['user_id'], data['activity_type'], data['duration_minutes'],
        data.get('distance_km'), data.get('calories_burned'),
        data.get('start_time'), data.get('end_time')
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Workout logged successfully'})


# --------------------------
# Get Workouts (GET)
# --------------------------
@app.route('/workouts/<int:user_id>', methods=['GET'])
def get_workouts(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workouts WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    workouts = [dict(zip(columns, row)) for row in rows]
    cursor.close()
    conn.close()
    return jsonify(workouts)


# --------------------------
# Log GPS Route (POST)
# --------------------------
@app.route('/gps', methods=['POST'])
def log_gps():
    data = request.json
    workout_id = data['workout_id']
    coordinates = data['coordinates']

    conn = get_db_connection()
    cursor = conn.cursor()
    for point in coordinates:
        cursor.execute("""
            INSERT INTO gps_routes (workout_id, latitude, longitude, timestamp)
            VALUES (?, ?, ?, ?)
        """, (workout_id, point['lat'], point['lng'], point['timestamp']))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'GPS data saved'})


# --------------------------
# Get GPS Routes (GET)
# --------------------------
@app.route('/gps/<int:workout_id>', methods=['GET'])
def get_gps(workout_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT latitude, longitude, timestamp FROM gps_routes WHERE workout_id = ?", (workout_id,))
    rows = cursor.fetchall()
    gps_data = [{'lat': row[0], 'lng': row[1], 'timestamp': row[2]} for row in rows]
    cursor.close()
    conn.close()
    return jsonify(gps_data)


# --------------------------
# Log Meal (POST)
# --------------------------
@app.route('/meals', methods=['POST'])
def log_meal():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meals (user_id, meal_type, description, calories, meal_time)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data['user_id'], data['meal_type'], data['description'],
        data['calories'], data['meal_time']
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Meal logged'})


# --------------------------
# Get Meals (GET)
# --------------------------
@app.route('/meals/<int:user_id>', methods=['GET'])
def get_meals(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meals WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    meals = [dict(zip(columns, row)) for row in rows]
    cursor.close()
    conn.close()
    return jsonify(meals)


# --------------------------
# Log Water (POST)
# --------------------------
@app.route('/water', methods=['POST'])
def log_water():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO water_intake (user_id, amount_ml, intake_time)
        VALUES (?, ?, ?)
    """, (
        data['user_id'], data['amount_ml'], data['intake_time']
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Water intake logged'})


# --------------------------
# Get Water Intake (GET)
# --------------------------
@app.route('/water/<int:user_id>', methods=['GET'])
def get_water(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM water_intake WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    water_logs = [dict(zip(columns, row)) for row in rows]
    cursor.close()
    conn.close()
    return jsonify(water_logs)


# --------------------------
# Set Goal (POST)
# --------------------------
@app.route('/goals', methods=['POST'])
def set_goal():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fitness_goals (user_id, goal_type, target_value, start_date, end_date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data['user_id'], data['goal_type'], data['target_value'],
        data['start_date'], data['end_date']
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Goal set'})


# --------------------------
# Get Goals (GET)
# --------------------------
@app.route('/goals/<int:user_id>', methods=['GET'])
def get_goals(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fitness_goals WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    goals = [dict(zip(columns, row)) for row in rows]
    cursor.close()
    conn.close()
    return jsonify(goals)


# --------------------------
# Health Check
# --------------------------
@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Fitness Tracker API is live 🔥'})


if __name__ == '__main__':
    app.run(debug=True)
