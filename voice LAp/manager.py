import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('leave_management.db')
cursor = conn.cursor()

# Query the leave applications table
cursor.execute("SELECT * FROM leave_application")
rows = cursor.fetchall()

# Display the results
for row in rows:
    print(row)

# Close the connection
conn.close()
