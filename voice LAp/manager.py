from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS to allow cross-origin requests

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
            to_date TEXT NOT NULL,
            status TEXT DEFAULT 'pending',  -- Default status is 'pending'
            description TEXT  -- Optional field for rejection reason
        )
    ''')
    connection.commit()
    connection.close()

init_db()

@app.route('/apply_leave', methods=['POST'])
def apply_leave():
    """
    Endpoint to apply for leave.
    """
    try:
        data = request.get_json()
        employee_name = data['employee_name']
        leave_type = data['leave_type']
        from_date = data['from_date']
        to_date = data['to_date']

        connection = sqlite3.connect('leave_applications.db')
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO leave_applications (employee_name, leave_type, from_date, to_date)
            VALUES (?, ?, ?, ?)
        ''', (employee_name, leave_type, from_date, to_date))
        connection.commit()
        connection.close()

        return jsonify({"message": "Leave application submitted successfully!"})

    except Exception as e:
        return jsonify({"detail": str(e)}), 400

@app.route('/get_leave_applications', methods=['GET'])
def get_leave_applications():
    """
    Endpoint to fetch all leave applications.
    """
    try:
        connection = sqlite3.connect('leave_applications.db')
        cursor = connection.cursor()

        # Fetch all leave applications
        cursor.execute('SELECT * FROM leave_applications')
        rows = cursor.fetchall()
        connection.close()

        # If there are no rows, return an empty list
        if not rows:
            return jsonify([])

        leave_applications = []
        for row in rows:
            # Ensure the row has the expected number of columns
            if len(row) >= 6:  # Adjust based on the number of columns in your table
                leave_applications.append({
                    "id": row[0],
                    "employee_name": row[1],
                    "leave_type": row[2],
                    "from_date": row[3],
                    "to_date": row[4],
                    "status": row[5],
                    "description": row[6] if len(row) > 6 else None  # Optional rejection reason
                })
            else:
                # Skip rows with missing columns
                continue

        return jsonify(leave_applications)

    except Exception as e:
        return jsonify({"detail": str(e)}), 400

    # """
    # Endpoint to fetch all leave applications.
    # """
    # try:
    #     connection = sqlite3.connect('leave_applications.db')
    #     cursor = connection.cursor()

    #     cursor.execute('SELECT * FROM leave_applications')
    #     rows = cursor.fetchall()
    #     connection.close()

    #     leave_applications = []
    #     for row in rows:
    #         leave_applications.append({
    #             "id": row[0],
    #             "employee_name": row[1],
    #             "leave_type": row[2],
    #             "from_date": row[3],
    #             "to_date": row[4],
    #             "status": row[5],
    #             "description": row[6]  # Optional rejection reason
    #         })

    #     return jsonify(leave_applications)

    # except Exception as e:
    #     return jsonify({"detail": str(e)}), 400

@app.route('/approve_leave', methods=['POST'])
def approve_leave():
    """
    Endpoint to approve a leave application.
    """
    try:
        data = request.get_json()
        application_id = data['id']

        # Update the status of the leave application to 'approved'
        connection = sqlite3.connect('leave_applications.db')
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE leave_applications
            SET status = ?
            WHERE id = ?
        ''', ('approved', application_id))
        connection.commit()
        connection.close()

        return jsonify({"message": "Leave application approved successfully!"})

    except Exception as e:
        return jsonify({"detail": str(e)}), 400

@app.route('/reject_leave', methods=['POST'])
def reject_leave():
    """
    Endpoint to reject a leave application with a reason.
    """
    try:
        data = request.get_json()
        application_id = data['id']
        description = data.get('description', 'No reason provided')  # Optional description

        # Update the status and description of the leave application to 'rejected'
        connection = sqlite3.connect('leave_applications.db')
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE leave_applications
            SET status = ?, description = ?
            WHERE id = ?
        ''', ('rejected', description, application_id))
        connection.commit()
        connection.close()

        return jsonify({"message": "Leave application rejected successfully!"})

    except Exception as e:
        return jsonify({"detail": str(e)}), 400

@app.route('/health_check', methods=['GET'])
def health_check():
    """
    Endpoint to check if the server is running.
    """
    return jsonify({"message": "Server is running!"})

if __name__ == '__main__':
    app.run(debug=True)
