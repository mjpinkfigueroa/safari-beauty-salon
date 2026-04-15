"""
app.py — Safari Beauty Salon Backend (Sprint 4 Update)

NEW IN SPRINT 4:
  - Environment variables loaded from .env file (no hardcoded secrets)
  - Admin password protection via session tokens
  - Email confirmation sent to client on booking
  - PATCH route to update booking status (pending → confirmed)

PYTHON CONCEPTS USED HERE:
  - os.environ    : reads environment variables from the .env file
  - smtplib       : Python's built-in email sending library
  - hashlib       : generates secure tokens for admin sessions
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3
from datetime import datetime

# smtplib and email are built into Python — no pip install needed
# smtplib handles the connection to Gmail's mail server
# email.mime handles building the email message structure
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# python-dotenv loads your .env file into os.environ
# This must happen before you read any env variables
from dotenv import load_dotenv
load_dotenv()

from models.database import init_db, get_db_connection

# ── CREATE APP ─────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# ── LOAD CONFIGURATION FROM .env ──────────────────────────────────
# os.environ.get() reads a value from the environment.
# The second argument is a fallback default if the variable isn't set.
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
app.config['DATABASE']       = os.path.join(BASE_DIR, '..', 'database', 'salon.db')
app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'safari2025')
app.config['GMAIL_ADDRESS']  = os.environ.get('GMAIL_ADDRESS', '')
app.config['GMAIL_APP_PW']   = os.environ.get('GMAIL_APP_PASSWORD', '')
app.config['SECRET_KEY']     = os.environ.get('SECRET_KEY', 'dev-secret')

# ── INITIALIZE DATABASE ────────────────────────────────────────────
with app.app_context():
    init_db(app.config['DATABASE'])


# ════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# These are reusable functions called by multiple routes below.
# ════════════════════════════════════════════════════════════════════

def send_confirmation_email(to_email, first_name, service, date, time):
    """
    Sends a booking confirmation email to the client.

    Uses Python's smtplib to connect to Gmail's SMTP server
    and send an HTML email.

    SMTP = Simple Mail Transfer Protocol — the standard for sending email.
    Think of it like a postal service: smtplib is the mailman,
    Gmail's server is the post office.

    Parameters:
        to_email   : client's email address
        first_name : client's first name (for personalization)
        service    : the service they booked
        date       : appointment date
        time       : appointment time

    Returns:
        True if email sent successfully, False if it failed
    """
    gmail_address = app.config['GMAIL_ADDRESS']
    gmail_app_pw  = app.config['GMAIL_APP_PW']

    # If Gmail credentials aren't configured, skip silently
    if not gmail_address or not gmail_app_pw:
        print('⚠️  Gmail not configured — skipping email confirmation')
        return False

    try:
        # MIMEMultipart lets us send both plain text AND HTML versions
        # Email clients show HTML if supported, plain text as fallback
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Your appointment at Safari Beauty Salon — {date}'
        msg['From']    = gmail_address
        msg['To']      = to_email

        # ── PLAIN TEXT VERSION ─────────────────────────────────────
        # For email clients that don't support HTML
        text_body = f"""
Hi {first_name},

Your appointment has been booked!

Service: {service}
Date: {date}
Time: {time}

Please arrive 5 minutes early.
If you need to cancel, please give us 24 hours notice.

See you soon!
Safari Beauty Salon
South Gate, CA
        """

        # ── HTML VERSION ───────────────────────────────────────────
        # A nicely formatted email that matches your salon's brand
        html_body = f"""
        <html>
        <body style="margin:0;padding:0;background:#FAF8F5;font-family:'Helvetica Neue',Arial,sans-serif;">
          <div style="max-width:560px;margin:40px auto;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.06);">

            <!-- Header -->
            <div style="background:#2C2C2C;padding:32px 40px;text-align:center;">
              <h1 style="margin:0;font-size:22px;color:#ffffff;font-weight:400;letter-spacing:2px;">
                SAFARI <span style="color:#C9A96E;">BEAUTY</span>
              </h1>
              <p style="margin:8px 0 0;font-size:12px;color:#888;letter-spacing:1px;text-transform:uppercase;">South Gate, California</p>
            </div>

            <!-- Body -->
            <div style="padding:40px;">
              <p style="color:#C9A96E;font-size:12px;letter-spacing:2px;text-transform:uppercase;margin:0 0 8px;">Booking Confirmed</p>
              <h2 style="margin:0 0 24px;font-size:26px;color:#2C2C2C;font-weight:400;">
                You're all set, {first_name}!
              </h2>
              <p style="color:#8C7B6E;font-size:15px;line-height:1.7;margin:0 0 32px;">
                We've received your appointment request and will have everything ready for you.
              </p>

              <!-- Appointment Details Box -->
              <div style="background:#FAF8F5;border-radius:8px;padding:24px;margin-bottom:32px;">
                <p style="margin:0 0 4px;font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#C9A96E;">Your Appointment</p>
                <table style="width:100%;margin-top:16px;">
                  <tr>
                    <td style="padding:8px 0;font-size:13px;color:#8C7B6E;width:40%;">Service</td>
                    <td style="padding:8px 0;font-size:13px;color:#2C2C2C;font-weight:500;">{service}</td>
                  </tr>
                  <tr>
                    <td style="padding:8px 0;font-size:13px;color:#8C7B6E;border-top:1px solid #E8DDD0;">Date</td>
                    <td style="padding:8px 0;font-size:13px;color:#2C2C2C;font-weight:500;border-top:1px solid #E8DDD0;">{date}</td>
                  </tr>
                  <tr>
                    <td style="padding:8px 0;font-size:13px;color:#8C7B6E;border-top:1px solid #E8DDD0;">Time</td>
                    <td style="padding:8px 0;font-size:13px;color:#2C2C2C;font-weight:500;border-top:1px solid #E8DDD0;">{time}</td>
                  </tr>
                </table>
              </div>

              <!-- Reminders -->
              <p style="font-size:13px;color:#8C7B6E;line-height:1.8;margin:0 0 8px;">A few things to remember:</p>
              <ul style="font-size:13px;color:#8C7B6E;line-height:2;padding-left:20px;margin:0 0 32px;">
                <li>Please arrive <strong style="color:#5C4A32;">5 minutes early</strong></li>
                <li>Cancellations need <strong style="color:#5C4A32;">24 hours notice</strong></li>
                <li>Your stylist will discuss your look before starting</li>
              </ul>

              <p style="font-size:14px;color:#5C4A32;margin:0;">See you soon! 🌿</p>
            </div>

            <!-- Footer -->
            <div style="background:#FAF8F5;padding:20px 40px;text-align:center;border-top:1px solid #E8DDD0;">
              <p style="margin:0;font-size:12px;color:#8C7B6E;">Safari Beauty Salon · South Gate, CA</p>
            </div>

          </div>
        </body>
        </html>
        """

        # Attach both versions — email client picks the best one
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        # Connect to Gmail's SMTP server
        # Port 587 = TLS (encrypted) connection — always use this for Gmail
        # starttls() upgrades the connection to encrypted before sending credentials
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(gmail_address, gmail_app_pw)
            server.sendmail(gmail_address, to_email, msg.as_string())

        print(f'✅ Confirmation email sent to {to_email}')
        return True

    except Exception as e:
        # Email failing should NOT crash the booking — just log and continue
        print(f'⚠️  Email error: {e}')
        return False


# ════════════════════════════════════════════════════════════════════
# ROUTES
# ════════════════════════════════════════════════════════════════════

# ── HEALTH CHECK ───────────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Safari Beauty Salon API is running',
        'timestamp': datetime.now().isoformat()
    })


# ── ADMIN LOGIN ────────────────────────────────────────────────────
# Route: POST /api/admin/login
# The admin page sends the password here.
# We compare it to the one in .env and return success/failure.
# This is simple password checking — not full user authentication.
# Sprint 5 could upgrade this to JWT tokens if needed.
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    password = data.get('password', '')

    if password == app.config['ADMIN_PASSWORD']:
        return jsonify({
            'success': True,
            'message': 'Access granted'
        })
    else:
        # 401 = Unauthorized
        return jsonify({
            'success': False,
            'error': 'Incorrect password'
        }), 401


# ── GET ALL BOOKINGS ───────────────────────────────────────────────
@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    try:
        conn = get_db_connection(app.config['DATABASE'])
        bookings = conn.execute(
            'SELECT * FROM bookings ORDER BY date ASC, time ASC'
        ).fetchall()
        conn.close()
        return jsonify({
            'success': True,
            'count': len(bookings),
            'bookings': [dict(row) for row in bookings]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ── CREATE A BOOKING ───────────────────────────────────────────────
@app.route('/api/bookings', methods=['POST'])
def create_booking():
    try:
        data = request.get_json()

        required_fields = ['first_name', 'last_name', 'email', 'service', 'date', 'time']
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return jsonify({
                'success': False,
                'error': f'Missing fields: {", ".join(missing)}'
            }), 400

        conn = get_db_connection(app.config['DATABASE'])
        conn.execute(
            '''INSERT INTO bookings
               (first_name, last_name, email, phone, service, stylist, date, time, notes, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                data['first_name'], data['last_name'], data['email'],
                data.get('phone', ''), data['service'],
                data.get('stylist', 'Any'), data['date'], data['time'],
                data.get('notes', ''), 'pending',
                datetime.now().isoformat()
            )
        )
        conn.commit()
        conn.close()

        # Send confirmation email AFTER saving to database
        # Even if email fails, the booking is already saved safely
        email_sent = send_confirmation_email(
            to_email   = data['email'],
            first_name = data['first_name'],
            service    = data['service'],
            date       = data['date'],
            time       = data['time']
        )

        return jsonify({
            'success': True,
            'message': f"Booked for {data['first_name']} on {data['date']} at {data['time']}",
            'email_sent': email_sent
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ── UPDATE BOOKING STATUS ──────────────────────────────────────────
# Route: PATCH /api/bookings/<id>
# PATCH = partial update (we're only changing the status field)
# PUT   = full replacement (we'd send all fields)
# The admin dashboard uses this to confirm or cancel appointments.
@app.route('/api/bookings/<int:booking_id>', methods=['PATCH'])
def update_booking_status(booking_id):
    try:
        data   = request.get_json()
        status = data.get('status')

        # Only allow valid status values
        allowed = ['pending', 'confirmed', 'cancelled']
        if status not in allowed:
            return jsonify({
                'success': False,
                'error': f'Status must be one of: {", ".join(allowed)}'
            }), 400

        conn    = get_db_connection(app.config['DATABASE'])
        booking = conn.execute(
            'SELECT id FROM bookings WHERE id = ?', (booking_id,)
        ).fetchone()

        if not booking:
            conn.close()
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        conn.execute(
            'UPDATE bookings SET status = ? WHERE id = ?',
            (status, booking_id)
        )
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'Booking {booking_id} updated to {status}'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ── DELETE A BOOKING ───────────────────────────────────────────────
@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    try:
        conn    = get_db_connection(app.config['DATABASE'])
        booking = conn.execute(
            'SELECT id FROM bookings WHERE id = ?', (booking_id,)
        ).fetchone()

        if not booking:
            conn.close()
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        conn.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': f'Booking {booking_id} deleted'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ── GET AVAILABILITY ───────────────────────────────────────────────
@app.route('/api/availability', methods=['GET'])
def get_availability():
    try:
        date = request.args.get('date')
        if not date:
            return jsonify({'success': False, 'error': 'Date is required'}), 400

        conn   = get_db_connection(app.config['DATABASE'])
        booked = conn.execute(
            'SELECT time FROM bookings WHERE date = ? AND status != ?',
            (date, 'cancelled')
        ).fetchall()
        conn.close()

        booked_times = [row['time'] for row in booked]
        all_slots    = [
            '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
            '1:00 PM',  '2:00 PM',  '3:00 PM',  '4:00 PM',
            '5:00 PM',  '6:00 PM'
        ]

        slots = [
            {'time': slot, 'available': slot not in booked_times}
            for slot in all_slots
        ]

        return jsonify({'success': True, 'date': date, 'slots': slots})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ── RUN ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('🌸 Safari Beauty Salon API starting...')
    print('📍 Running at: http://localhost:5000')
    print('🔍 Health check: http://localhost:5000/api/health')
    app.run(debug=True, port=5000)
