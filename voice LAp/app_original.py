from flask import Flask,render_template, request, jsonify
from flask_cors import CORS  # Import CORS for cross-origin support
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

# Initialize the database and table
def init_db():
    connection = sqlite3.connect('leave_applications.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leave_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            from_date TEXT NOT NULL,
            to_date TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()

init_db()

@app.route('/apply_leave', methods=['POST'])
def apply_leave():
    try:
        data = request.get_json()  # Get JSON data from the frontend
        employee_name = data['employee_name']
        leave_type = data['leave_type']
        from_date = data['from_date']
        to_date = data['to_date']

        # Check if any field is empty
        if not all([employee_name, leave_type, from_date, to_date]):
            return jsonify({"detail": "All fields (employee_name, leave_type, from_date, to_date) are required."}), 400

        connection = sqlite3.connect('leave_applications.db')
        cursor = connection.cursor()

        # Insert the leave application into the database
        cursor.execute('''
            INSERT INTO leave_applications (employee_name, leave_type, from_date, to_date)
            VALUES (?, ?, ?, ?)
        ''', (employee_name, leave_type, from_date, to_date))

        connection.commit()
        connection.close()

        return jsonify({"message": "Leave application submitted successfully!"})

    except Exception as e:
        # Handle any unexpected errors and return a message
        return jsonify({"detail": str(e)}), 400

@app.route('/get_leave_applications', methods=['GET'])
def get_leave_applications():
    try:
        connection = sqlite3.connect('leave_applications.db')
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM leave_applications')
        rows = cursor.fetchall()
        connection.close()

        leave_applications = []
        for row in rows:
            leave_applications.append({
                "id": row[0],
                "employee_name": row[1],
                "leave_type": row[2],
                "from_date": row[3],
                "to_date": row[4]
            })

        return jsonify(leave_applications)

    except Exception as e:
        return jsonify({"detail": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
