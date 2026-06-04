# 🌊 AquaSplash – Smart Water Park Ticket System

A full-stack ticket management and administration dashboard built with Python (Flask), MySQL, and a modern frontend using Alpine.js and Tailwind CSS.

---

## 📁 Project Structure

```text
aquasplash/
├── app.py                  ← Flask backend server
├── requirements.txt        ← Python dependencies
├── .gitignore              ← Ignored files
└── templates/
    └── index.html          ← Frontend UI Dashboard
    
⚡ Quick Start
1. Database Setup (MySQL)
This project requires a local MySQL server.

Create a database named water_park.

Update the connection string in app.py if your local MySQL credentials differ:
mysql+pymysql://root:MyNewPassword@localhost/water_park

2. Install Dependencies
Bash
pip install -r requirements.txt
3. Run the Server
The application will automatically initialize the database tables and default data on the first run.

Bash
python app.py
4. Access the Dashboard
Visit: http://127.0.0.1:5000

Default Admin Username: admin

Default Admin Password: admin123

🎟️ Core Features
📱 Instant QR Code Ticket Generation
The system features a seamless point-of-sale interface for generating digital tickets on the fly:

Dynamic Ticket Selection: Choose from multiple dynamically priced tiers (e.g., Toddler Splash, General Admission).

Guest Registration: Capture essential guest details (Name, Email, Phone, Visit Date).

Automated QR Generation: Instantly process the booking to generate a unique Ticket ID and a scannable QR code.

E-Ticket Download: Export the generated QR pass as an image file for easy distribution to the guest.

🔍 Gate Validation & Scanning
Built-in HTML5 QR scanner to validate entries via webcam.

Fallback manual ID entry for quick validation.

Real-time validation checks against the database to prevent duplicate entries or invalid dates.

📊 Live Operations Dashboard
Real-time metrics for total tickets sold, revenue tracking, and live check-ins.

Attraction Management: Easily toggle individual ride statuses (Open / Closed / Maintenance) from the operations panel.

🛠️ Tech Stack
Backend: Python 3, Flask, SQLAlchemy, PyMySQL, Flask-Login

Frontend: HTML5, Tailwind CSS, Alpine.js, HTML5-QRCode

Ticket Generation: qrcode (Python), Canvas API (JavaScript)

Database: MySQL