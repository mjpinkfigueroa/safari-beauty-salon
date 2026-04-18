🌿 Safari Beauty Salon
A full-stack web application built for a real local beauty salon in South Gate, California.
Features a modern multi-page website, online appointment booking system, email confirmations,
and a password-protected admin dashboard for the salon owner.
🌐 Live Site: safari-beauty-salon.netlify.app
⚙️ API: safari-beauty-salon-api.onrender.com

📸 Preview

Homepage with real salon photo, booking form, and admin dashboard.

✨ Features

Multi-page responsive website — Home, Services, Gallery, Booking, About, Contact
Online appointment booking — clients select service, stylist, date, and time
Real-time availability — booked time slots are grayed out automatically
Email confirmations — clients receive a branded HTML confirmation email on booking
Admin dashboard — password-protected portal for the salon owner to manage appointments
Booking status management — owner can confirm, cancel, or delete appointments
Mobile responsive — works on all screen sizes
Continuous deployment — pushing to GitHub auto-deploys frontend and backend


🛠️ Tech Stack
LayerTechnologyPurposeFrontendHTML, CSS, JavaScriptMulti-page website UIBackendPython, FlaskREST API serverDatabaseSQLiteAppointment storageEmailGmail SMTP / smtplibBooking confirmationsFrontend HostingNetlifyStatic site deploymentBackend HostingRenderPython server deploymentVersion ControlGit + GitHubSource control & CI/CD

📁 Project Structure
safari-beauty-salon/
│
├── frontend/                  # Static website
│   ├── index.html             # Homepage
│   ├── services.html          # Services & pricing
│   ├── gallery.html           # Photo gallery
│   ├── booking.html           # Appointment booking form
│   ├── about.html             # Salon story & remodel
│   ├── contact.html           # Contact form & info
│   ├── admin.html             # Owner dashboard (password protected)
│   ├── css/
│   │   └── style.css          # Global stylesheet with CSS variables
│   ├── js/
│   │   ├── main.js            # Shared JS (nav, animations)
│   │   └── booking.js         # Booking form → API connection
│   └── assets/                # Salon photos
│
├── backend/                   # Python Flask API
│   ├── app.py                 # Main server & all routes
│   ├── requirements.txt       # Python dependencies
│   └── models/
│       ├── __init__.py        # Package marker
│       └── database.py        # SQLite setup & helpers
│
├── database/                  # Created automatically on first run
│   └── salon.db               # SQLite database file
│
├── docs/                      # Project documentation
├── .gitignore                 # Ignores venv, .env, database
└── README.md                  # This file

🚀 Running Locally
Prerequisites

Python 3.x
Git

Setup
1. Clone the repository
bashgit clone https://github.com/mjpinkfigueroa/safari-beauty-salon.git
cd safari-beauty-salon
2. Create and activate virtual environment
bash# Windows
python -m venv venv
venv\Scripts\Activate.ps1

# Mac/Linux
python -m venv venv
source venv/bin/activate
3. Install Python dependencies
bashpip install -r backend/requirements.txt
4. Create environment variables file
Create a .env file in the project root:
ADMIN_PASSWORD=your_admin_password
GMAIL_ADDRESS=your.gmail@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
SECRET_KEY=your_secret_key
5. Start the backend server
bashpython backend/app.py
Server runs at http://localhost:5000
6. Open the frontend
Open frontend/index.html with Live Server in VS Code.

🔌 API Endpoints
MethodEndpointDescriptionGET/api/healthHealth checkGET/api/bookingsGet all appointmentsPOST/api/bookingsCreate new appointmentPATCH/api/bookings/<id>Update booking statusDELETE/api/bookings/<id>Delete a bookingGET/api/availability?date=YYYY-MM-DDGet available time slotsPOST/api/admin/loginAdmin authentication

📋 Agile Sprint Plan
SprintGoalStatus1Project setup, GitHub, documentation✅ Complete2Static frontend — all 6 pages✅ Complete3Python backend + SQLite + booking API✅ Complete4Admin login, email confirmations, status updates✅ Complete5Deployment — Netlify + Render✅ Complete6Polish, documentation, handoff✅ Complete

💡 Key Concepts Demonstrated

REST API design — proper HTTP methods (GET, POST, PATCH, DELETE)
Database design — SQLite schema with bookings and services tables
Environment variables — secrets never hardcoded, loaded from .env
CORS configuration — cross-origin requests between frontend and backend
Email automation — HTML email templates via Python smtplib
Agile methodology — project managed with GitHub Projects board
CI/CD — automatic deployment on every GitHub push
Responsive design — CSS Grid, Flexbox, mobile-first media queries
DOM manipulation — dynamic rendering of availability and booking data


👤 Author
Jennifer Perdomo

📄 License
This project was built for Safari Beauty Salon, South Gate, CA.
