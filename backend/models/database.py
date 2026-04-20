"""
database.py — Database helper functions
Safari Beauty Salon — Sprint 7: PostgreSQL upgrade

Switched from SQLite to PostgreSQL (Supabase).
The logic is identical — only the connection method changes.

SQLite:   sqlite3.connect('salon.db')          — local file
Postgres: psycopg2.connect(DATABASE_URL)       — cloud database
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    """
    Opens a connection to the PostgreSQL database on Supabase.

    RealDictCursor makes rows behave like dictionaries:
      row['first_name'] instead of row[0]

    The DATABASE_URL comes from the environment variable
    set in .env locally and in Render's dashboard on the server.
    """
    database_url = os.environ.get('DATABASE_URL')

    if not database_url:
        raise Exception('DATABASE_URL environment variable is not set.')

    conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return conn


def init_db():
    """
    Creates the database tables if they don't exist yet.
    Runs once when the Flask server starts.

    PostgreSQL uses SERIAL instead of SQLite's AUTOINCREMENT.
    TEXT and INTEGER types work the same in both.
    """
    conn = get_db_connection()
    cur  = conn.cursor()

    # Bookings table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id          SERIAL PRIMARY KEY,
            first_name  TEXT NOT NULL,
            last_name   TEXT NOT NULL,
            email       TEXT NOT NULL,
            phone       TEXT,
            service     TEXT NOT NULL,
            stylist     TEXT,
            date        TEXT NOT NULL,
            time        TEXT NOT NULL,
            notes       TEXT,
            status      TEXT DEFAULT 'pending',
            created_at  TEXT NOT NULL
        )
    ''')

    # Services table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id          SERIAL PRIMARY KEY,
            category    TEXT NOT NULL,
            name        TEXT NOT NULL,
            description TEXT,
            price_from  INTEGER NOT NULL,
            duration    TEXT
        )
    ''')

    # Seed services only if table is empty
    cur.execute('SELECT COUNT(*) FROM services')
    count = cur.fetchone()['count']

    if count == 0:
        services_data = [
            ('Haircuts',    "Women's Haircut",    'Wash, cut, and blow-dry',           45,  '60 min'),
            ('Haircuts',    "Men's Haircut",       'Precision cut with clean finish',   30,  '30 min'),
            ('Haircuts',    "Kids' Haircut",       'For kids 12 and under',             20,  '30 min'),
            ('Haircuts',    'Bang Trim',            'Quick bang refresh',                10,  '15 min'),
            ('Extensions',  'Tape-In Extensions',  'Seamless, reusable tape method',   200,  '2 hrs'),
            ('Extensions',  'Sew-In Extensions',   'Weft sewn onto braided base',      250,  '3 hrs'),
            ('Extensions',  'Extension Removal',   'Safe removal with conditioning',    75,  '60 min'),
            ('Color',       'Full Color',           'Single-process root to ends',       85,  '90 min'),
            ('Color',       'Highlights',           'Partial or full foil highlights',  100,  '2 hrs'),
            ('Color',       'Balayage',             'Hand-painted natural color',        130,  '2.5 hrs'),
            ('Color',       'Root Touch-Up',        'Color at root only',                60,  '60 min'),
            ('Treatments',  'Keratin Treatment',    'Frizz-free smoothing',             150,  '2.5 hrs'),
            ('Treatments',  'Deep Conditioning',    'Intensive moisture mask',            35,  '45 min'),
        ]

        cur.executemany(
            '''INSERT INTO services (category, name, description, price_from, duration)
               VALUES (%s, %s, %s, %s, %s)''',
            services_data
        )

    conn.commit()
    cur.close()
    conn.close()
    print('✅ PostgreSQL database initialized successfully')
