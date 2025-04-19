from app.db import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Import AuditLog for migration/discovery

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    phone_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # OTP registration fields
    otp_hash = db.Column(db.String(64), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    otp_attempts = db.Column(db.Integer, default=0)
    otp_last_requested = db.Column(db.DateTime, nullable=True)
    otp_lockout_until = db.Column(db.DateTime, nullable=True)
    # Device/network fingerprinting
    device_fingerprint = db.Column(db.String(64), nullable=True)
    registration_ip = db.Column(db.String(45), nullable=True)
    registration_location = db.Column(db.String(128), nullable=True)
    # OTP verification failure tracking
    failed_otp_attempts = db.Column(db.Integer, default=0)
    last_otp_failure = db.Column(db.DateTime, nullable=True)
    # User role (user/admin)
    role = db.Column(db.String(16), default='user')
    # Add more fields as needed (e.g., risk_level, etc.)
