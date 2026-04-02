from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
import uuid
import qrcode
import io
import base64
from datetime import datetime, date, timedelta
import os

app = Flask(__name__)
CORS(app, supports_credentials=True) # Required for session cookies
app.secret_key = "amusement_park_secret_2024" # Must be changed in production

# ─── Database Configuration ───────────────────────────────────────────────────
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:MyNewPassword@localhost/amusement_park'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─── Authentication Configuration ─────────────────────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Unauthorized access. Admin login required."}), 401

# ─── Models ───────────────────────────────────────────────────────────────────

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    ticket_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    visit_date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')
    total_price = db.Column(db.Float, nullable=False)
    booked_at = db.Column(db.String(30), nullable=False)
    qr_code = db.Column(db.Text)
    checked_in = db.Column(db.Integer, default=0)
    checkin_time = db.Column(db.String(30))

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Ride(db.Model):
    __tablename__ = 'rides'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='open')
    wait_time = db.Column(db.Integer, default=0)
    capacity = db.Column(db.Integer, default=50)
    min_height = db.Column(db.Integer, default=0)
    thrill_level = db.Column(db.String(20), default='moderate')
    description = db.Column(db.Text)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class TicketType(db.Model):
    __tablename__ = 'ticket_types'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(20), default='#ff6b35')
    icon = db.Column(db.String(10), default='🎟️')

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# ─── Database Initialization ──────────────────────────────────────────────────

def init_db():
    db.create_all()

    # Seed default admin if missing
    if Admin.query.count() == 0:
        default_admin = Admin(username="admin")
        default_admin.set_password("admin123") # Change this immediately in production
        db.session.add(default_admin)

    if TicketType.query.count() == 0:
        types = [
            TicketType(name="Child (3-12 yrs)", price=599.0, description="Access to all child-friendly rides", color="#4ecdc4", icon="🧒"),
            TicketType(name="Adult (13-59 yrs)", price=999.0, description="Full park access with all rides", color="#ff6b35", icon="🎢"),
            TicketType(name="Senior (60+ yrs)", price=699.0, description="Full park access with priority queuing", color="#a8dadc", icon="👴"),
            TicketType(name="Family Pack (2+2)", price=2999.0, description="2 Adults + 2 Children with 10% discount", color="#e63946", icon="👨‍👩‍👧‍👦"),
            TicketType(name="VIP Pass", price=3999.0, description="Skip-the-line + premium lounge access", color="#ffd700", icon="⭐")
        ]
        db.session.bulk_save_objects(types)

    if Ride.query.count() == 0:
        rides = [
            Ride(name="Dragon Coaster", category="Thrill", status="open", wait_time=15, capacity=80, min_height=140, thrill_level="extreme", description="India's fastest steel roller coaster"),
            Ride(name="Splash Canyon", category="Water", status="open", wait_time=20, capacity=60, min_height=110, thrill_level="moderate", description="White water rafting adventure"),
            Ride(name="Sky Drop", category="Thrill", status="open", wait_time=10, capacity=40, min_height=150, thrill_level="extreme", description="Free-fall from 60 meters high"),
            Ride(name="Merry-Go-Round", category="Kids", status="open", wait_time=5, capacity=30, min_height=0, thrill_level="mild", description="Classic carousel for all ages"),
            Ride(name="Haunted Mansion", category="Adventure", status="open", wait_time=25, capacity=50, min_height=100, thrill_level="moderate", description="Spine-chilling ghost house"),
            Ride(name="Bumper Cars", category="Fun", status="open", wait_time=8, capacity=40, min_height=120, thrill_level="mild", description="Classic bumper car arena"),
            Ride(name="Giant Ferris Wheel", category="Scenic", status="open", wait_time=12, capacity=60, min_height=0, thrill_level="mild", description="360° panoramic view of the park"),
            Ride(name="Tornado Twister", category="Thrill", status="maintenance", wait_time=0, capacity=70, min_height=130, thrill_level="high", description="Spinning high-speed adventure"),
            Ride(name="Mini Train", category="Kids", status="open", wait_time=3, capacity=50, min_height=0, thrill_level="mild", description="Scenic train ride around the park"),
            Ride(name="Virtual Reality Zone", category="Tech", status="open", wait_time=18, capacity=30, min_height=0, thrill_level="moderate", description="Immersive VR gaming experience")
        ]
        db.session.bulk_save_objects(rides)
        
    db.session.commit()

# ─── Helper: Generate QR Code ─────────────────────────────────────────────────

def generate_qr(data: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a1a2e", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

# ── Auth Routes ───────────────────────────────────────────────────────────────

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "Missing credentials"}), 400
        
    user = Admin.query.filter_by(username=data["username"]).first()
    if user and user.check_password(data["password"]):
        login_user(user)
        return jsonify({"success": True, "message": "Logged in successfully"})
        
    return jsonify({"error": "Invalid username or password"}), 401

@app.route("/api/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True, "message": "Logged out successfully"})

@app.route("/api/check-auth")
def check_auth():
    if current_user.is_authenticated:
        return jsonify({"authenticated": True, "username": current_user.username})
    return jsonify({"authenticated": False}), 401

# ── Public Routes ─────────────────────────────────────────────────────────────

@app.route("/api/ticket-types")
def get_ticket_types():
    types = TicketType.query.all()
    return jsonify([t.to_dict() for t in types])

@app.route("/api/book", methods=["POST"])
def book_ticket():
    data = request.get_json()
    required = ["name", "email", "ticket_type_id", "quantity", "visit_date"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"'{field}' is required"}), 400

    ttype = TicketType.query.get(data["ticket_type_id"])
    if not ttype:
        return jsonify({"error": "Invalid ticket type"}), 400

    ticket_id = str(uuid.uuid4())[:8].upper()
    quantity = int(data["quantity"])
    total_price = ttype.price * quantity
    booked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    qr_data = f"TICKET:{ticket_id}|{data['name']}|{data['visit_date']}|{ttype.name}"
    qr_code_b64 = generate_qr(qr_data)

    new_ticket = Ticket(
        id=ticket_id,
        name=data["name"],
        email=data["email"],
        phone=data.get("phone", ""),
        ticket_type=ttype.name,
        quantity=quantity,
        visit_date=data["visit_date"],
        status="active",
        total_price=total_price,
        booked_at=booked_at,
        qr_code=qr_code_b64
    )

    db.session.add(new_ticket)
    db.session.commit()

    return jsonify({
        "success": True,
        "ticket": new_ticket.to_dict(),
        "message": f"Ticket booked! ID: {ticket_id}"
    })

# ── Protected Admin Routes ────────────────────────────────────────────────────

@app.route("/api/tickets")
@login_required
def get_tickets():
    status = request.args.get("status", "")
    search = request.args.get("search", "")
    
    query = Ticket.query
    if status:
        query = query.filter_by(status=status)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Ticket.name.ilike(search_pattern)) | 
            (Ticket.email.ilike(search_pattern)) | 
            (Ticket.id.ilike(search_pattern))
        )
        
    tickets = query.order_by(Ticket.booked_at.desc()).all()
    return jsonify([t.to_dict() for t in tickets])

@app.route("/api/tickets/<ticket_id>")
@login_required
def get_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id.upper())
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    return jsonify(ticket.to_dict())

@app.route("/api/checkin/<ticket_id>", methods=["POST"])
@login_required
def checkin(ticket_id):
    ticket = Ticket.query.get(ticket_id.upper())
    
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    if ticket.checked_in:
        return jsonify({"error": "Ticket already checked in", "checkin_time": ticket.checkin_time}), 400
    if ticket.status != "active":
        return jsonify({"error": f"Ticket is {ticket.status}"}), 400

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ticket.checked_in = 1
    ticket.checkin_time = now
    
    db.session.commit()
    return jsonify({"success": True, "message": "Check-in successful!", "checkin_time": now})

@app.route("/api/cancel/<ticket_id>", methods=["POST"])
@login_required
def cancel_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id.upper())
    
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    if ticket.status == "cancelled":
        return jsonify({"error": "Ticket already cancelled"}), 400
        
    ticket.status = 'cancelled'
    db.session.commit()
    return jsonify({"success": True, "message": "Ticket cancelled successfully"})

@app.route("/api/rides")
@login_required
def get_rides():
    rides = Ride.query.order_by(Ride.category, Ride.name).all()
    return jsonify([r.to_dict() for r in rides])

@app.route("/api/rides/<int:ride_id>/status", methods=["POST"])
@login_required
def update_ride_status(ride_id):
    data = request.get_json()
    status = data.get("status")
    
    if status not in ("open", "closed", "maintenance"):
        return jsonify({"error": "Invalid status"}), 400
        
    ride = Ride.query.get(ride_id)
    if not ride:
        return jsonify({"error": "Ride not found"}), 404
        
    ride.status = status
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/stats")
@login_required
def get_stats():
    today = date.today().isoformat()
    
    total_tickets = Ticket.query.count()
    active_tickets = Ticket.query.filter_by(status='active').count()
    checked_in = Ticket.query.filter_by(checked_in=1).count()
    cancelled = Ticket.query.filter_by(status='cancelled').count()
    
    today_bookings = Ticket.query.filter(Ticket.booked_at.startswith(today)).count()
    
    total_revenue_query = db.session.query(func.sum(Ticket.total_price)).filter(Ticket.status != 'cancelled').scalar()
    total_revenue = float(total_revenue_query) if total_revenue_query else 0.0
    
    today_revenue_query = db.session.query(func.sum(Ticket.total_price)).filter(Ticket.booked_at.startswith(today), Ticket.status != 'cancelled').scalar()
    today_revenue = float(today_revenue_query) if today_revenue_query else 0.0

    by_type_query = db.session.query(
        Ticket.ticket_type,
        func.count(Ticket.id).label('count'),
        func.sum(Ticket.total_price).label('revenue')
    ).filter(Ticket.status != 'cancelled').group_by(Ticket.ticket_type).all()
    
    by_type = [{"ticket_type": row.ticket_type, "count": row.count, "revenue": float(row.revenue or 0)} for row in by_type_query]

    six_days_ago = (date.today() - timedelta(days=6)).isoformat()
    daily_query = db.session.query(
        func.substr(Ticket.booked_at, 1, 10).label('day'),
        func.count(Ticket.id).label('count'),
        func.sum(Ticket.total_price).label('revenue')
    ).filter(
        func.substr(Ticket.booked_at, 1, 10) >= six_days_ago,
        Ticket.status != 'cancelled'
    ).group_by('day').order_by('day').all()
    
    daily = [{"day": row.day, "count": row.count, "revenue": float(row.revenue or 0)} for row in daily_query]

    open_rides = Ride.query.filter_by(status='open').count()
    total_rides = Ride.query.count()

    return jsonify({
        "total_tickets": total_tickets,
        "active_tickets": active_tickets,
        "checked_in": checked_in,
        "cancelled": cancelled,
        "today_bookings": today_bookings,
        "total_revenue": round(total_revenue, 2),
        "today_revenue": round(today_revenue, 2),
        "by_type": by_type,
        "daily_bookings": daily,
        "open_rides": open_rides,
        "total_rides": total_rides,
    })

# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    
    with app.app_context():
        init_db()
        
    print("=" * 55)
    print("  🎢  Smart Amusement Park Ticket System (Production Ready)")
    print("  🌐  http://127.0.0.1:5000")
    print("  🔑  Default Admin Login: admin / admin123")
    print("=" * 55)
    app.run(debug=True, port=5000)