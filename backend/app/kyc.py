from app.db import db
from datetime import datetime

class KYCSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(16), default='pending_manual')  # pending, approved, rejected
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    result = db.Column(db.String(64), nullable=True)
    documents = db.Column(db.Text, nullable=True)  # JSON or comma-separated paths/urls
    notes = db.Column(db.Text, nullable=True)



