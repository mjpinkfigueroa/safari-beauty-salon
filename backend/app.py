"""
app.py — Safari Beauty Salon Backend
Sprint 7: Switched from SQLite to PostgreSQL (Supabase)

Key difference from SQLite:
  - %s placeholders instead of ? for query parameters
  - conn.cursor() needed to execute queries
  - cursor must be closed after use
  - RealDictCursor returns rows as dicts automatically
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

from models.database import init_db, get_db_connection

app = Flask(__name__)
CORS(app)

app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'safari2025')
app.config['GMAIL_ADDRESS']  = os.environ.get('GMAIL_ADDRESS', '')
app.config['GMAIL_APP_PW']   = os.environ.get('GMAIL_APP_PASSWORD', '')

# Initialize database on startup
with app.app_context():
    init_db()


# ── EMAIL ──────────────────────────────────────────────────────────
def send_confirmation_email(to_email, first_name, service, date, time):
    gmail_address = app.config['GMAIL_ADDRESS']
    gmail_app_pw  = app.config['GMAIL_APP_PW']

    if not gmail_address or not gmail_app_pw:
        print('⚠️  Gmail not configured — skipping email')
        return False

    try:
        msg            = MIMEMultipart('alternative')
        msg['Subject'] = f'Your appointment at Safari Beauty Salon — {date}'
        msg['From']    = gmail_address
        msg['To']      = to_email

        text_body = f"""
Hi {first_name},

Your appointment has been booked!

Service: {service}
Date: {date}
Time: {time}

Please arrive 5 minutes early.
Cancellations require 24 hours notice.

See you soon!
Safari Beauty Salon — South Gate, CA
        """

        html_body = f"""
        <html>
        <body style="margin:0;padding:0;background:#F8F8F8;font-family:'Helvetica Neue',Arial,sans-serif;">
          <div style="max-width:560px;margin:40px auto;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
            <div style="background:#1A1A1A;padding:32px 40px;text-align:center;">
              <h1 style="margin:0;font-size:22px;color:#ffffff;font-weight:400;letter-spacing:2px;">
                SAFARI <span style="color:#B0926A;">BEAUTY SALON</span>
              </h1>
              <p style="margin:8px 0 0;font-size:12px;color:#888;letter-spacing:1px;text-transform:uppercase;">South Gate, California</p>
            </div>
            <div style="padding:40px;">
              <p style="color:#8A8A8A;font-size:12px;letter-spacing:2px;text-transform:uppercase;margin:0 0 8px;">Booking Confirmed</p>
              <h2 style="margin:0 0 24px;font-size:26px;color:#1A1A1A;font-weight:400;">You're all set, {first_name}!</h2>
              <p style="color:#8A8A8A;font-size:15px;line-height:1.7;margin:0 0 32px;">
                We've received your appointment and will have everything ready for you.
              </p>
              <div style="background:#F8F8F8;border-radius:8px;padding:24px;margin-bottom:32px;">
                <p style="margin:0 0 4px;font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#B0926A;">Your Appointment</p>
                <table style="width:100%;margin-top:16px;">
                  <tr>
                    <td style="padding:8px 0;font-size:13px;color:#8A8A8A;width:40%;">Service</td>
                    <td style="padding:8px 0;font-size:13px;color:#1A1A1A;font-weight:500;">{service}</td>
                  </tr>
                  <tr>
                    <td style="padding:8px 0;font-size:13px;color:#8A8A8A;border-top:1px solid #E0E0E0;">Date</td>
                    <td style="padding:8px 0;font-size:13px;color:#1A1A1A;font-weight:500;border-top:1px solid #E0E0E0;">{date}</td>
                  </tr>
                  <tr>
                    <td style="padding:8px 0;font-size:13px;color:#8A8A8A;border-top:1px solid #E0E0E0;">Time</td>
                    <td style="padding:8px 0;font-size:13px;color:#1A1A1A;font-weight:500;border-top:1px solid #E0E0E0;">{time}</td>
                  </tr>
                </table>
              </div>
              <ul style="font-size:13px;color:#8A8A8A;line-height:2;padding-left:20px;margin:0 0 32px;">
                <li>Please arrive <strong style="color:#2C2C2C;">5 minutes early</strong></li>
                <li>Cancellations need <strong style="color:#2C2C2C;">24 hours notice</strong></li>
                <li>Your stylist will discuss your look before starting</li>
              </ul>
              <p style="font-size:14px;color:#2C2C2C;margin:0;">See you soon!</p>
            </div>
            <div style="background:#F8F8F8;padding:20px 40px;text-align:center;border-top:1px solid #E0E0E0;">
              <p style="margin:0;font-size:12px;color:#8A8A8A;">Safari Beauty Salon · South Gate, CA</p>
            </div>
          </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(gmail_address, gmail_app_pw)
            server.sendmail(gmail_address, to_email, msg.as_string())

        print(f'✅ Confirmation email sent to {to_email}')
        return True

    except Exception as e:
        print(f'⚠️  Email error: {e}')
        return False


# ── ROUTES ─────────────────────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Safari Beauty Salon API is running (PostgreSQL)',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data     = request.get_json()
    password = data.get('password', '')

    if password == app.config['ADMIN_PASSWORD']:
        return jsonify({'success': True, 'message': 'Access granted'})
    return jsonify({'success': False, 'error': 'Incorrect password'}), 401


@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute('SELECT * FROM bookings ORDER BY date ASC, time ASC')
        bookings = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify({
            'success':  True,
            'count':    len(bookings),
            'bookings': [dict(b) for b in bookings]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/bookings', methods=['POST'])
def create_booking():
    try:
        data = request.get_json()

        required = ['first_name', 'last_name', 'email', 'service', 'date', 'time']
        missing  = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({'success': False, 'error': f'Missing fields: {", ".join(missing)}'}), 400

        conn = get_db_connection()
        cur  = conn.cursor()

        # PostgreSQL uses %s placeholders instead of SQLite's ?
        cur.execute(
            '''INSERT INTO bookings
               (first_name, last_name, email, phone, service, stylist, date, time, notes, status, created_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            (
                data['first_name'], data['last_name'], data['email'],
                data.get('phone', ''), data['service'],
                data.get('stylist', 'Any'), data['date'], data['time'],
                data.get('notes', ''), 'pending',
                datetime.now().isoformat()
            )
        )

        conn.commit()
        cur.close()
        conn.close()

        email_sent = send_confirmation_email(
            to_email   = data['email'],
            first_name = data['first_name'],
            service    = data['service'],
            date       = data['date'],
            time       = data['time']
        )

        return jsonify({
            'success':    True,
            'message':    f"Booked for {data['first_name']} on {data['date']} at {data['time']}",
            'email_sent': email_sent
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/bookings/<int:booking_id>', methods=['PATCH'])
def update_booking_status(booking_id):
    try:
        data    = request.get_json()
        status  = data.get('status')
        allowed = ['pending', 'confirmed', 'cancelled']

        if status not in allowed:
            return jsonify({'success': False, 'error': f'Status must be one of: {", ".join(allowed)}'}), 400

        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute('SELECT id FROM bookings WHERE id = %s', (booking_id,))

        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        cur.execute('UPDATE bookings SET status = %s WHERE id = %s', (status, booking_id))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'success': True, 'message': f'Booking {booking_id} updated to {status}'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    try:
        conn = get_db_connection()
        cur  = conn.cursor()
        cur.execute('SELECT id FROM bookings WHERE id = %s', (booking_id,))

        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        cur.execute('DELETE FROM bookings WHERE id = %s', (booking_id,))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'success': True, 'message': f'Booking {booking_id} deleted'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/availability', methods=['GET'])
def get_availability():
    try:
        date = request.args.get('date')
        if not date:
            return jsonify({'success': False, 'error': 'Date is required'}), 400

        conn   = get_db_connection()
        cur    = conn.cursor()
        cur.execute(
            "SELECT time FROM bookings WHERE date = %s AND status != 'cancelled'",
            (date,)
        )
        booked = cur.fetchall()
        cur.close()
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


if __name__ == '__main__':
    print('🌸 Safari Beauty Salon API starting...')
    print('📍 Running at: http://localhost:5000')
    print('🗄️  Database: PostgreSQL (Supabase)')
    app.run(debug=True, port=5000)
