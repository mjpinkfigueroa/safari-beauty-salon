"""
app.py — The main entry point for the Safari Beauty Salon backend server.

HOW FLASK WORKS:
Flask is a "web framework" — it lets Python listen for HTTP requests
(like when a browser submits a form) and send back responses.

When you run this file with `python app.py`, Python starts a local
web server at http://localhost:5000. Your frontend (HTML) sends
requests to this address, and Flask handles them.

ROUTE = a URL path that Flask knows how to respond to.
Example: @app.route('/api/bookings') handles requests to /api/bookings
"""

# ── IMPORTS ───────────────────────────────────────────────────────
# Flask: the web framework
# request: lets us read data sent from the browser
# jsonify: converts Python dicts to JSON responses
from flask import Flask, request, jsonify

# CORS: Cross-Origin Resource Sharing
# Allows our frontend (on one port) to talk to our backend (on another port)
# Without this, browsers block requests between different origins for security
from flask_cors import CORS

# os: built-in Python module for file path operations
import os

# datetime: built-in Python module for working with dates and times
from datetime import datetime

# Import our database helper functions (we'll create this file next)
from models.database import init_db, get_db_connection

# ── CREATE THE FLASK APP ───────────────────────────────────────────
# Flask(__name__) creates the app.
# __name__ is a special Python variable that holds the current file's name.
# Flask uses it to find resources relative to this file.
app = Flask(__name__)

# Apply CORS to the entire app — allows all origins for now.
# In production, you'd restrict this to your actual domain.
CORS(app)

# ── CONFIGURATION ─────────────────────────────────────────────────
# Where to store our SQLite database file
# os.path.dirname gets the folder this file is in
# os.path.join builds a path safely (handles / vs \ on different OS)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['DATABASE'] = os.path.join(BASE_DIR, '..', 'database', 'salon.db')


# ── INITIALIZE DATABASE ────────────────────────────────────────────
# This runs once when the app starts.
# It creates the database file and tables if they don't exist yet.
with app.app_context():
    init_db(app.config['DATABASE'])


# ════════════════════════════════════════════════════════════════
# ROUTES
# A route is a URL path + a Python function that handles it.
# The @app.route decorator tells Flask which URL triggers which function.
# ════════════════════════════════════════════════════════════════


# ── HEALTH CHECK ──────────────────────────────────────────────────
# Route: GET /api/health
# Purpose: A simple way to confirm the server is running.
# Open http://localhost:5000/api/health in your browser to test it.
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Safari Beauty Salon API is running',
        'timestamp': datetime.now().isoformat()
    })


# ── GET ALL BOOKINGS ───────────────────────────────────────────────
# Route: GET /api/bookings
# Purpose: Returns all appointments from the database.
# Used by the admin dashboard to display all bookings.
@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    try:
        conn = get_db_connection(app.config['DATABASE'])

        # fetchall() returns all rows as a list
        # We convert each row to a dict so jsonify can handle it
        bookings = conn.execute(
            'SELECT * FROM bookings ORDER BY date ASC, time ASC'
        ).fetchall()
        conn.close()

        # Convert sqlite3.Row objects to plain Python dicts
        bookings_list = [dict(row) for row in bookings]

        return jsonify({
            'success': True,
            'count': len(bookings_list),
            'bookings': bookings_list
        })

    except Exception as e:
        # If something goes wrong, return an error response
        # str(e) converts the error object to a readable string
        return jsonify({'success': False, 'error': str(e)}), 500


# ── CREATE A BOOKING ───────────────────────────────────────────────
# Route: POST /api/bookings
# Purpose: Receives form data and saves a new appointment.
# The frontend sends data here when the user submits the booking form.
@app.route('/api/bookings', methods=['POST'])
def create_booking():
    try:
        # request.get_json() reads the JSON data sent from the browser
        data = request.get_json()

        # ── VALIDATION ──────────────────────────────────────────
        # Always validate data before saving it to a database.
        # Never trust that the browser sent what you expect.
        required_fields = ['first_name', 'last_name', 'email', 'service', 'date', 'time']
        missing = [field for field in required_fields if not data.get(field)]

        if missing:
            # 400 = Bad Request (the client sent incomplete data)
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing)}'
            }), 400

        # ── SAVE TO DATABASE ─────────────────────────────────────
        conn = get_db_connection(app.config['DATABASE'])

        # ? placeholders prevent SQL injection attacks
        # Never put user data directly into SQL strings
        conn.execute(
            '''INSERT INTO bookings
               (first_name, last_name, email, phone, service, stylist, date, time, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                data['first_name'],
                data['last_name'],
                data['email'],
                data.get('phone', ''),          # .get() returns '' if key missing
                data['service'],
                data.get('stylist', 'Any'),
                data['date'],
                data['time'],
                data.get('notes', ''),
                datetime.now().isoformat()       # record when booking was made
            )
        )

        # commit() saves the changes — without this, nothing is actually written
        conn.commit()
        conn.close()

        # 201 = Created (standard HTTP status for successfully creating a resource)
        return jsonify({
            'success': True,
            'message': f"Appointment booked for {data['first_name']} on {data['date']} at {data['time']}"
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ── DELETE A BOOKING ───────────────────────────────────────────────
# Route: DELETE /api/bookings/<id>
# Purpose: Removes a booking by its ID (used in the admin dashboard).
# <int:booking_id> captures the number from the URL.
# Example: DELETE /api/bookings/3 → booking_id = 3
@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    try:
        conn = get_db_connection(app.config['DATABASE'])

        # First check the booking actually exists
        booking = conn.execute(
            'SELECT id FROM bookings WHERE id = ?', (booking_id,)
        ).fetchone()

        if not booking:
            conn.close()
            # 404 = Not Found
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        conn.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Booking {booking_id} deleted'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ── GET AVAILABLE TIME SLOTS ───────────────────────────────────────
# Route: GET /api/availability?date=2025-06-15&stylist=any
# Purpose: Returns which time slots are already booked for a given date.
# The frontend uses this to gray out unavailable times.
@app.route('/api/availability', methods=['GET'])
def get_availability():
    try:
        # request.args reads URL query parameters (?date=...&stylist=...)
        date = request.args.get('date')
        stylist = request.args.get('stylist', 'any')

        if not date:
            return jsonify({'success': False, 'error': 'Date is required'}), 400

        conn = get_db_connection(app.config['DATABASE'])

        # Find all booked times for the given date
        booked = conn.execute(
            'SELECT time FROM bookings WHERE date = ?', (date,)
        ).fetchall()
        conn.close()

        booked_times = [row['time'] for row in booked]

        # All possible time slots
        all_slots = [
            '9:00 AM', '10:00 AM', '11:00 AM',
            '12:00 PM', '1:00 PM', '2:00 PM',
            '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM'
        ]

        # Build response showing which slots are available
        slots = [
            {'time': slot, 'available': slot not in booked_times}
            for slot in all_slots
        ]

        return jsonify({
            'success': True,
            'date': date,
            'slots': slots
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ── RUN THE SERVER ─────────────────────────────────────────────────
# This block only runs when you execute this file directly
# (not when it's imported by another file).
# debug=True means Flask restarts automatically when you save changes —
# very useful during development. Turn this OFF before deploying.
if __name__ == '__main__':
    print('🌸 Safari Beauty Salon API starting...')
    print('📍 Running at: http://localhost:5000')
    print('🔍 Health check: http://localhost:5000/api/health')
    app.run(debug=True, port=5000)
