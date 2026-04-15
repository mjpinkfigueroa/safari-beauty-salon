"""
database.py — Database helper functions
Safari Beauty Salon

This file handles everything related to the SQLite database:
- Creating the database and tables (init_db)
- Opening a connection to the database (get_db_connection)

WHY SQLite?
SQLite is a database that lives in a single .db file on your computer.
It's perfect for learning and small projects because:
  - No separate server to install or run
  - The entire database is one file
  - Python has built-in support for it (sqlite3 module)
  
For production (a live website), we'd switch to PostgreSQL,
but the Python code stays almost identical — just the connection changes.

HOW A DATABASE WORKS (simplified):
Think of it like Excel. A database has:
  - Tables  = spreadsheet tabs
  - Columns = spreadsheet columns (Name, Date, etc.)
  - Rows    = individual entries (one appointment per row)
"""

# sqlite3 is built into Python — no pip install needed
import sqlite3


def get_db_connection(db_path):
    """
    Opens a connection to the SQLite database file.
    
    Parameters:
        db_path (str): The file path to the .db file
    
    Returns:
        conn: A database connection object
    
    Think of this like opening a spreadsheet file.
    You need to open it before you can read or write data.
    Always close it when you're done (conn.close()).
    """
    conn = sqlite3.connect(db_path)

    # row_factory lets us access columns by name instead of index.
    # Without it:  row[0], row[1], row[2]...  (confusing)
    # With it:     row['first_name'], row['date']  (clear!)
    conn.row_factory = sqlite3.Row

    return conn


def init_db(db_path):
    """
    Creates the database tables if they don't exist yet.
    
    This runs once when the server starts. If the tables already exist,
    "CREATE TABLE IF NOT EXISTS" safely skips creation — no duplicates.
    
    Parameters:
        db_path (str): The file path where the .db file should be created
    """
    conn = get_db_connection(db_path)

    # ── BOOKINGS TABLE ────────────────────────────────────────────
    # Stores every appointment made through the website.
    # Each column has a TYPE and optional CONSTRAINTS:
    #   INTEGER PRIMARY KEY AUTOINCREMENT = unique ID, auto-numbered
    #   TEXT NOT NULL = required text field
    #   TEXT = optional text field
    conn.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
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

    # ── SERVICES TABLE ────────────────────────────────────────────
    # Stores the salon's service menu.
    # Seeded with starter data below so the frontend can fetch it dynamically.
    conn.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT NOT NULL,
            name        TEXT NOT NULL,
            description TEXT,
            price_from  INTEGER NOT NULL,
            duration    TEXT
        )
    ''')

    # ── SEED SERVICES DATA ────────────────────────────────────────
    # "Seeding" means inserting starter data into a fresh database.
    # We only do this if the services table is empty.
    existing = conn.execute('SELECT COUNT(*) FROM services').fetchone()[0]

    if existing == 0:
        services_data = [
            # (category, name, description, price_from, duration)
            ('Haircuts', "Women's Haircut", 'Wash, cut, and blow-dry', 45, '60 min'),
            ('Haircuts', "Men's Haircut",   'Precision cut with clean finish', 30, '30 min'),
            ('Haircuts', "Kids' Haircut",   'For kids 12 and under', 20, '30 min'),
            ('Haircuts', 'Bang Trim',        'Quick bang refresh', 10, '15 min'),
            ('Extensions', 'Tape-In Extensions', 'Seamless, reusable tape method', 200, '2 hrs'),
            ('Extensions', 'Sew-In Extensions',  'Weft sewn onto braided base', 250, '3 hrs'),
            ('Extensions', 'Extension Removal',  'Safe removal with conditioning', 75, '60 min'),
            ('Color', 'Full Color',      'Single-process root to ends', 85, '90 min'),
            ('Color', 'Highlights',      'Partial or full foil highlights', 100, '2 hrs'),
            ('Color', 'Balayage',        'Hand-painted natural color', 130, '2.5 hrs'),
            ('Color', 'Root Touch-Up',   'Color at root only', 60, '60 min'),
            ('Treatments', 'Keratin Treatment', 'Frizz-free smoothing', 150, '2.5 hrs'),
            ('Treatments', 'Deep Conditioning', 'Intensive moisture mask', 35, '45 min'),
        ]

        # executemany() inserts multiple rows at once — more efficient than a loop
        conn.executemany(
            '''INSERT INTO services (category, name, description, price_from, duration)
               VALUES (?, ?, ?, ?, ?)''',
            services_data
        )

    # commit() saves all changes to the file
    conn.commit()
    conn.close()

    print(f'✅ Database initialized at: {db_path}')
