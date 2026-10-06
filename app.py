from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import datetime, timedelta
from functools import wraps
import os
import smtplib
from email.message import EmailMessage


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "safeher-ai-secret-key-change-later"
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
os.makedirs(DATABASE_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DATABASE_DIR, "safeher.db")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DATABASE_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ============================================================
# DATABASE MODELS
# ============================================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), nullable=False, unique=True)

    emergency_contact = db.Column(db.String(100), nullable=True)
    emergency_email = db.Column(db.String(150), nullable=True)

    password = db.Column(db.String(255), nullable=False)

    contacts = db.relationship(
        "EmergencyContact",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    locations = db.relationship(
        "LiveLocation",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    timers = db.relationship(
        "SafetyTimer",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


class EmergencyContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(150), nullable=True)


class LiveLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class SafetyTimer(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    duration_minutes = db.Column(db.Integer, nullable=False)

    started_at = db.Column(
        db.DateTime,
        nullable=False
    )

    expires_at = db.Column(
        db.DateTime,
        nullable=False
    )

    active = db.Column(
        db.Boolean,
        default=True
    )

    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

with app.app_context():
    db.create_all()


# ============================================================
# LOGIN HELPER
# ============================================================

def login_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return decorated_function


def current_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    return db.session.get(User, user_id)


# ============================================================
# EMAIL
# ============================================================

def get_contact_emails(user):

    emails = []

    if not user:
        return emails

    contacts = EmergencyContact.query.filter_by(
        user_id=user.id
    ).all()

    for contact in contacts:

        if contact.email:
            email = contact.email.strip()

            if email and email not in emails:
                emails.append(email)

    # Backward compatibility with registration emergency email
    if user.emergency_email:

        email = user.emergency_email.strip()

        if email and email not in emails:
            emails.append(email)

    return emails


def send_email_alert(receivers, subject, body):

    if not receivers:
        print("No emergency contact email addresses found.")
        return False

    sender = os.environ.get("SAFEHER_EMAIL")
    password = os.environ.get("SAFEHER_EMAIL_PASSWORD")

    if not sender or not password:
        print("Email credentials are not configured.")
        return False

    try:

        message = EmailMessage()

        message["Subject"] = subject
        message["From"] = sender
        message["To"] = ", ".join(receivers)

        message.set_content(body)

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as server:

            server.login(
                sender,
                password
            )

            server.send_message(message)

        print("Emergency email sent to:", receivers)

        return True

    except Exception as error:

        print("EMAIL ERROR:", error)

        return False


def send_sos_alert(user, latitude=None, longitude=None, reason="SOS"):

    receivers = get_contact_emails(user)

    if not receivers:
        print("No trusted contacts available.")
        return False

    if latitude is not None and longitude is not None:

        maps_link = (
            f"https://www.google.com/maps?q="
            f"{latitude},{longitude}"
        )

        location_text = (
            f"Latitude: {latitude}\n"
            f"Longitude: {longitude}\n"
            f"Google Maps: {maps_link}"
        )

    else:

        location_text = "Location was not available."

    body = f"""
SAFEHER AI EMERGENCY ALERT

Alert Type:
{reason}

User:
{user.name}

Phone:
{user.phone}

Time:
{datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")}

Location:
{location_text}

Please check on the user immediately.

This alert was generated by SafeHer AI.
"""

    subject = f"🚨 SafeHer AI Emergency Alert - {reason}"

    return send_email_alert(
        receivers,
        subject,
        body
    )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():

    return render_template("index.html")


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        emergency_contact = request.form.get(
            "emergency_contact",
            ""
        ).strip()

        emergency_email = request.form.get(
            "emergency_email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not name or not phone or not password:

            flash(
                "Please fill all required fields.",
                "error"
            )

            return render_template("register.html")

        existing_user = User.query.filter_by(
            phone=phone
        ).first()

        if existing_user:

            flash(
                "A user with this phone number already exists.",
                "error"
            )

            return render_template("register.html")

        new_user = User(
            name=name,
            phone=phone,
            emergency_contact=emergency_contact,
            emergency_email=emergency_email,
            password=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("register.html")


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        user = User.query.filter_by(
            phone=phone
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            session.clear()

            session["user_id"] = user.id
            session["user_name"] = user.name

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid phone number or password.",
            "error"
        )

    return render_template("login.html")


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user = current_user()

    contacts = EmergencyContact.query.filter_by(
        user_id=user.id
    ).all()

    active_timer = SafetyTimer.query.filter_by(
        user_id=user.id,
        active=True
    ).order_by(
        SafetyTimer.id.desc()
    ).first()

    latest_location = LiveLocation.query.filter_by(
        user_id=user.id
    ).order_by(
        LiveLocation.updated_at.desc()
    ).first()

    return render_template(
        "dashboard.html",
        user=user,
        contacts=contacts,
        active_timer=active_timer,
        latest_location=latest_location
    )


# ============================================================
# SOS PAGE
# ============================================================

@app.route("/sos", methods=["GET", "POST"])
@login_required
def sos():

    user = current_user()

    if request.method == "POST":

        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")

        try:

            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None

        except ValueError:

            latitude = None
            longitude = None

        success = send_sos_alert(
            user,
            latitude,
            longitude,
            "SOS Button"
        )

        if success:

            flash(
                "Emergency alert sent to trusted contacts.",
                "success"
            )

        else:

            flash(
                "SOS triggered, but the email alert could not be sent.",
                "error"
            )

        return redirect(
            url_for("sos_success")
        )

    return render_template(
        "sos.html",
        user=user
    )


@app.route("/sos_success")
@login_required
def sos_success():

    return render_template(
        "sos_success.html"
    )


# ============================================================
# QUICK SOS
# ============================================================

@app.route("/send_sos", methods=["POST"])
@login_required
def send_sos():

    user = current_user()

    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")

    try:

        latitude = float(latitude)
        longitude = float(longitude)

    except (TypeError, ValueError):

        return jsonify({
            "success": False,
            "message": "Valid GPS location is required."
        }), 400

    success = send_sos_alert(
        user,
        latitude,
        longitude,
        "Quick SOS"
    )

    if success:

        return jsonify({
            "success": True,
            "message": "Emergency alert sent successfully."
        })

    return jsonify({
        "success": False,
        "message": "SOS triggered, but email could not be sent."
    }), 500


# ============================================================
# UPDATE LIVE LOCATION
# ============================================================

@app.route("/update_location", methods=["POST"])
@login_required
def update_location():

    data = request.get_json(
        silent=True
    ) or {}

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    try:

        latitude = float(latitude)
        longitude = float(longitude)

    except (TypeError, ValueError):

        return jsonify({
            "success": False,
            "message": "Invalid location."
        }), 400

    user = current_user()

    location = LiveLocation(
        user_id=user.id,
        latitude=latitude,
        longitude=longitude,
        updated_at=datetime.utcnow()
    )

    db.session.add(location)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Location updated."
    })


# ============================================================
# LIVE MAP
# ============================================================

@app.route("/live_map")
@login_required
def live_map():

    user = current_user()

    latest_location = LiveLocation.query.filter_by(
        user_id=user.id
    ).order_by(
        LiveLocation.updated_at.desc()
    ).first()

    return render_template(
        "live_map.html",
        location=latest_location
    )


# ============================================================
# EMERGENCY CONTACTS
# ============================================================

@app.route("/emergency_contacts", methods=["GET", "POST"])
@login_required
def emergency_contacts():

    user = current_user()

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        if not name:

            flash(
                "Contact name is required.",
                "error"
            )

            return redirect(
                url_for("emergency_contacts")
            )

        contact = EmergencyContact(
            user_id=user.id,
            name=name,
            phone=phone,
            email=email
        )

        db.session.add(contact)
        db.session.commit()

        flash(
            "Trusted contact added.",
            "success"
        )

        return redirect(
            url_for("emergency_contacts")
        )

    contacts = EmergencyContact.query.filter_by(
        user_id=user.id
    ).all()

    return render_template(
        "emergency_contacts.html",
        contacts=contacts,
        user=user
    )


@app.route(
    "/delete_contact/<int:contact_id>",
    methods=["POST"]
)
@login_required
def delete_contact(contact_id):

    user = current_user()

    contact = EmergencyContact.query.filter_by(
        id=contact_id,
        user_id=user.id
    ).first()

    if contact:

        db.session.delete(contact)
        db.session.commit()

        flash(
            "Trusted contact removed.",
            "success"
        )

    return redirect(
        url_for("emergency_contacts")
    )


# ============================================================
# SAFETY TIMER
# ============================================================

@app.route("/safety_timer")
@login_required
def safety_timer():

    user = current_user()

    active_timer = SafetyTimer.query.filter_by(
        user_id=user.id,
        active=True
    ).order_by(
        SafetyTimer.id.desc()
    ).first()

    return render_template(
        "safety_timer.html",
        active_timer=active_timer,
        user=user
    )


@app.route(
    "/start_safety_timer",
    methods=["POST"]
)
@login_required
def start_safety_timer():

    user = current_user()

    duration = request.form.get(
        "duration",
        "5"
    )

    try:

        duration = int(duration)

    except ValueError:

        return jsonify({
            "success": False,
            "message": "Invalid timer duration."
        }), 400

    allowed_durations = [
        5,
        10,
        20,
        30,
        60
    ]

    if duration not in allowed_durations:

        return jsonify({
            "success": False,
            "message": "Invalid timer duration."
        }), 400

    # Deactivate old timers
    old_timers = SafetyTimer.query.filter_by(
        user_id=user.id,
        active=True
    ).all()

    for timer in old_timers:
        timer.active = False

    now = datetime.utcnow()

    timer = SafetyTimer(
        user_id=user.id,
        duration_minutes=duration,
        started_at=now,
        expires_at=now + timedelta(
            minutes=duration
        ),
        active=True
    )

    db.session.add(timer)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Safety Timer started for {duration} minutes.",
        "timer_id": timer.id,
        "expires_at": timer.expires_at.isoformat()
    })


@app.route(
    "/check_in_timer",
    methods=["POST"]
)
@login_required
def check_in_timer():

    user = current_user()

    timer = SafetyTimer.query.filter_by(
        user_id=user.id,
        active=True
    ).order_by(
        SafetyTimer.id.desc()
    ).first()

    if not timer:

        return jsonify({
            "success": False,
            "message": "No active safety timer."
        }), 404

    now = datetime.utcnow()

    if now >= timer.expires_at:

        timer.active = False
        db.session.commit()

        send_sos_alert(
            user,
            timer.latitude,
            timer.longitude,
            "Safety Timer Expired"
        )

        return jsonify({
            "success": False,
            "expired": True,
            "message": "Timer already expired."
        })

    timer.active = False

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Check-in successful. You are safe."
    })


@app.route(
    "/cancel_safety_timer",
    methods=["POST"]
)
@login_required
def cancel_safety_timer():

    user = current_user()

    timer = SafetyTimer.query.filter_by(
        user_id=user.id,
        active=True
    ).order_by(
        SafetyTimer.id.desc()
    ).first()

    if not timer:

        return jsonify({
            "success": False,
            "message": "No active timer."
        }), 404

    timer.active = False

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Safety Timer cancelled."
    })


@app.route(
    "/safety_timer_expired",
    methods=["POST"]
)
@login_required
def safety_timer_expired():

    user = current_user()

    timer = SafetyTimer.query.filter_by(
        user_id=user.id,
        active=True
    ).order_by(
        SafetyTimer.id.desc()
    ).first()

    if not timer:

        return jsonify({
            "success": False,
            "message": "No active timer."
        }), 404

    now = datetime.utcnow()

    if now < timer.expires_at:

        return jsonify({
            "success": False,
            "message": "Timer has not expired yet."
        })

    timer.active = False

    db.session.commit()

    success = send_sos_alert(
        user,
        timer.latitude,
        timer.longitude,
        "Safety Timer Expired"
    )

    return jsonify({
        "success": success,
        "expired": True,
        "message": (
            "Timer expired and trusted contacts were alerted."
            if success
            else
            "Timer expired, but the email alert could not be sent."
        )
    })


@app.route(
    "/save_timer_location",
    methods=["POST"]
)
@login_required
def save_timer_location():

    user = current_user()

    data = request.get_json(
        silent=True
    ) or {}

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    try:

        latitude = float(latitude)
        longitude = float(longitude)

    except (TypeError, ValueError):

        return jsonify({
            "success": False,
            "message": "Invalid location."
        }), 400

    timer = SafetyTimer.query.filter_by(
        user_id=user.id,
        active=True
    ).order_by(
        SafetyTimer.id.desc()
    ).first()

    if not timer:

        return jsonify({
            "success": False,
            "message": "No active timer."
        }), 404

    timer.latitude = latitude
    timer.longitude = longitude

    db.session.commit()

    return jsonify({
        "success": True
    })


# ============================================================
# VOICE SOS
# ============================================================

@app.route("/voice_sos")
@login_required
def voice_sos():

    return render_template(
        "voice_sos.html"
    )


# ============================================================
# FAKE CALL
# ============================================================

@app.route("/fake_call")
@login_required
def fake_call():

    return render_template(
        "fake_call.html"
    )


# ============================================================
# SAFEHER ASSISTANT
# ============================================================

@app.route("/assistant")
@login_required
def assistant():

    return render_template(
        "assistant.html"
    )


@app.route(
    "/assistant_reply",
    methods=["POST"]
)
@login_required
def assistant_reply():

    data = request.get_json(
        silent=True
    ) or {}

    message = data.get(
        "message",
        ""
    ).strip().lower()

    if not message:

        return jsonify({
            "reply": "Please tell me how I can help you."
        })

    if any(
        word in message
        for word in [
            "sos",
            "emergency",
            "danger",
            "help"
        ]
    ):

        reply = (
            "If you are in immediate danger, use the SOS button "
            "to alert your trusted contacts and share your location."
        )

    elif "timer" in message:

        reply = (
            "Safety Timer lets you set a countdown. "
            "Check in before it expires. If you do not check in, "
            "SafeHer AI can trigger an emergency alert."
        )

    elif (
        "location" in message
        or "where am i" in message
    ):

        reply = (
            "Open Live Location and allow browser location access "
            "to update and view your current location."
        )

    elif (
        "contact" in message
        or "contacts" in message
    ):

        reply = (
            "Open Trusted Contacts to add the people who should "
            "receive your emergency alerts."
        )

    elif (
        "voice" in message
        or "speak" in message
    ):

        reply = (
            "Voice SOS uses your browser's speech recognition "
            "while the Voice SOS page is open."
        )

    elif (
        "call" in message
        or "fake call" in message
    ):

        reply = (
            "Fake Call provides a simulated incoming-call screen "
            "to help you create a distraction."
        )

    else:

        reply = (
            "I can help with SOS, Safety Timer, Live Location, "
            "Trusted Contacts, Voice SOS and other SafeHer features."
        )

    return jsonify({
        "reply": reply
    })


# ============================================================
# NEARBY HELP
# ============================================================

@app.route("/nearby_help")
@login_required
def nearby_help():

    return render_template(
        "nearby_help.html"
    )


# ============================================================
# SAFE ROUTE BACKEND
# ============================================================
# Kept only for compatibility with old files.
# It will NOT be shown on the new dashboard.

@app.route("/safe_route")
@login_required
def safe_route():

    return render_template(
        "safe_route.html"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "app": "SafeHer AI"
    })


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return (
        render_template(
            "index.html"
        ),
        404
    )


@app.errorhandler(500)
def internal_server_error(error):

    db.session.rollback()

    return (
        "SafeHer AI encountered a server error.",
        500
    )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 50)
    print("          SAFEHER AI SERVER")
    print("=" * 50)
    print()
    print("Database:")
    print(DATABASE_PATH)
    print()
    print("Server:")
    print("http://127.0.0.1:5000")
    print()
    print("=" * 50)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )