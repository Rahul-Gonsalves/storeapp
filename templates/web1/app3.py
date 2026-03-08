# app.py
from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# --- Database Configuration ---
db_config = {
    'host': 'localhost',
    'database': 'flask_api_db',
    'user': 'root',      # <-- IMPORTANT: Change to your MySQL username
    'password': 'pass' # <-- IMPORTANT: Change to your MySQL password
}

# --- Helper Function to get DB connection ---
def get_db_connection():
    """Establishes a connection to the database."""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

# --- API Endpoints ---

# GET /tasks -> Retrieve all tasks
@app.route('/api/v1/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True) # dictionary=True returns rows as dicts
    cursor.execute("SELECT id, title, description, done FROM tasks")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'tasks': tasks})

# GET /tasks/<id> -> Retrieve a single task
@app.route('/api/v1/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title, description, done FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    cursor.close()
    conn.close()

    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify({'task': task})

# POST /tasks -> Create a new task
@app.route('/api/v1/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'title' in request.json:
        return jsonify({'error': 'Bad Request: Missing title in request body'}), 400

    new_task_data = {
        'title': request.json['title'],
        'description': request.json.get('description', "")
    }

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    query = "INSERT INTO tasks (title, description) VALUES (%s, %s)"
    cursor.execute(query, (new_task_data['title'], new_task_data['description']))
    new_id = cursor.lastrowid
    conn.commit() # Commit the transaction to save the change
    cursor.close()
    conn.close()

    # Fetch the newly created task to return it
    new_task = {'id': new_id, 'done': False, **new_task_data}
    return jsonify({'task': new_task}), 201

# PUT /tasks/<id> -> Update an existing task
@app.route('/api/v1/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    if not request.json:
        return jsonify({'error': 'Bad Request: No data provided'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)

    # First, check if the task exists
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    if task is None:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    # Update fields if they are in the request JSON
    update_data = {
        'title': request.json.get('title', task['title']),
        'description': request.json.get('description', task['description']),
        'done': request.json.get('done', task['done'])
    }

    query = "UPDATE tasks SET title = %s, description = %s, done = %s WHERE id = %s"
    cursor.execute(query, (update_data['title'], update_data['description'], update_data['done'], task_id))
    conn.commit()

    # Fetch the updated task to return it
    cursor.execute("SELECT id, title, description, done FROM tasks WHERE id = %s", (task_id,))
    updated_task = cursor.fetchone()
    cursor.close()
    conn.close()

    return jsonify({'task': updated_task})

# DELETE /tasks/<id> -> Delete a task
@app.route('/api/v1/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()
    # Check if the task exists before deleting
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Task not found'}), 404

    # If it exists, delete it
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return '', 204 # 204 No Content is standard for successful deletion

if __name__ == '__main__':
    app.run(debug=True)