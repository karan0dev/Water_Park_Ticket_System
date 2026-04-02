# 🎢 FunWorld – Smart Amusement Park Ticket System

A full-stack ticket management system with Python (Flask) backend + HTML/CSS/JS frontend.

---

## 📁 Project Structure

```
amusement_park/
├── app.py                  ← Flask backend (run this)
├── requirements.txt        ← Python dependencies
├── tickets.db              ← SQLite database (auto-created)
└── templates/
    └── index.html          ← Frontend UI
```

---

## ⚡ Quick Start (VS Code)

### 1. Install Python dependencies
Open a terminal in VS Code and run:
```bash
pip install -r requirements.txt
```

### 2. Run the server
```bash
python app.py
```

### 3. Open in browser
Visit: **http://127.0.0.1:5000**

---

## 🎟️ Features

| Feature | Description |
|---|---|
| **Dashboard** | Live stats — tickets, revenue, check-ins, ride status |
| **Book Ticket** | 5 ticket types, QR code generated instantly |
| **All Tickets** | Search, filter, cancel, check-in |
| **Lookup / Check-in** | Search by ID, scan details, one-click check-in |
| **Rides Status** | View & toggle ride status (Open / Closed / Maintenance) |

### Ticket Types
- 🧒 Child (₹599) · 🎢 Adult (₹999) · 👴 Senior (₹699)
- 👨‍👩‍👧‍👦 Family Pack 2+2 (₹2,999) · ⭐ VIP Pass (₹3,999)

---

## 🔌 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/ticket-types` | All ticket categories |
| POST | `/api/book` | Book a new ticket |
| GET | `/api/tickets` | All tickets (filter/search) |
| GET | `/api/tickets/<id>` | Single ticket detail |
| POST | `/api/checkin/<id>` | Check-in visitor |
| POST | `/api/cancel/<id>` | Cancel a ticket |
| GET | `/api/rides` | Ride list & status |
| POST | `/api/rides/<id>/status` | Update ride status |
| GET | `/api/stats` | Dashboard statistics |

---

## 🛠️ Tech Stack
- **Backend**: Python 3 · Flask · SQLite · qrcode
- **Frontend**: Vanilla HTML/CSS/JS (no framework needed)
- **Database**: Auto-seeded SQLite (10 rides, 5 ticket types)
