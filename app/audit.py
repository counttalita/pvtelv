from app.db import db
from datetime import datetime

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(32), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    ip = db.Column(db.String(45), nullable=True)
    device_fingerprint = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(16), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.String(256), nullable=True)


def log_audit(event_type, phone, ip, device_fingerprint, status, details=None):
    entry = AuditLog(
        event_type=event_type,
        phone=phone,
        ip=ip,
        device_fingerprint=device_fingerprint,
        status=status,
        details=details
    )
    db.session.add(entry)
    db.session.commit()
