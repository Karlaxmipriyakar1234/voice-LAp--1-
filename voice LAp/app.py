from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leave_management.db'  # Path to your database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the LeaveApplication model
class LeaveApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)
    from_date = db.Column(db.String(10), nullable=False)
    to_date = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<LeaveApplication {self.id}, {self.employee_name}, {self.leave_type}>"

# Create the database and table if it doesn't exist
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Welcome to the Voice Leave Management App!"

@app.route('/manager_review')
def manager_review():
    return render_template('manager.html')

@app.route('/voice_application')
def voice_application():
    return render_template('index.html')

@app.route('/get_leave_applications', methods=['GET'])
def get_leave_applications():
    leave_applications = LeaveApplication.query.all()  # Get all leave applications from the DB
    applications = []
    for app in leave_applications:
        applications.append({
            "id": app.id,
            "employee_name": app.employee_name,
            "leave_type": app.leave_type,
            "from_date": app.from_date,
            "to_date": app.to_date,
            "status": app.status
        })
    return jsonify(applications)

@app.route('/approve_leave', methods=['POST'])
def approve_leave():
    data = request.json
    leave_id = data.get('id')

    application = LeaveApplication.query.get(leave_id)
    if application:
        application.status = 'Approved'
        db.session.commit()
        return jsonify({"message": "Leave approved successfully!"})

    return jsonify({"message": "Leave application not found."}), 404

@app.route('/reject_leave', methods=['POST'])
def reject_leave():
    data = request.json
    leave_id = data.get('id')
    description = data.get('description')

    application = LeaveApplication.query.get(leave_id)
    if application:
        application.status = f"Rejected: {description}"
        db.session.commit()
        return jsonify({"message": "Leave rejected successfully!"})

    return jsonify({"message": "Leave application not found."}), 404

@app.route('/apply_leave', methods=['POST'])
def apply_leave():
    data = request.json
    employee_name = data.get('employee_name')
    leave_type = data.get('leave_type')
    from_date = data.get('from_date')
    to_date = data.get('to_date')

    if not (employee_name and leave_type and from_date and to_date):
        return jsonify({"detail": "All fields are required."}), 400

    new_application = LeaveApplication(
        employee_name=employee_name,
        leave_type=leave_type,
        from_date=from_date,
        to_date=to_date,
        status=None  # Initially, the status will be None
    )

    try:
        db.session.add(new_application)
        db.session.commit()  # Commit the transaction to save it to the database
        print(f"New leave application added: {new_application}")
        return jsonify({"message": "Leave application submitted successfully!"})
    except Exception as e:
        db.session.rollback()  # Rollback the transaction if something goes wrong
        print(f"Error adding leave application: {e}")
        return jsonify({"message": "An error occurred while submitting the application."}), 500

if __name__ == '__main__':
    app.run(debug=False)
