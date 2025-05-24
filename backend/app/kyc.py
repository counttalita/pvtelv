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

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'result': self.result,
            'documents': self.documents, # Assuming documents is a simple string or JSON serializable
            'notes': self.notes
        }

