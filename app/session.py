from app.models import db
from datetime import datetime

class ActiveSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    device_fingerprint = db.Column(db.String(64), nullable=False)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)


def create_session(user_id, device_fingerprint, jti, expires_at):
    session = ActiveSession(user_id=user_id, device_fingerprint=device_fingerprint, jti=jti, expires_at=expires_at)
    db.session.add(session)
    db.session.commit()
    return session


def revoke_session(jti):
    session = ActiveSession.query.filter_by(jti=jti).first()
    if session:
        session.revoked = True
        db.session.commit()
        return True
    return False


def refresh_session(jti, new_expiry):
    session = ActiveSession.query.filter_by(jti=jti, revoked=False).first()
    if session:
        session.expires_at = new_expiry
        session.last_seen = datetime.utcnow()
        db.session.commit()
        return True
    return False


def is_session_active(jti):
    session = ActiveSession.query.filter_by(jti=jti, revoked=False).first()
    if not session or session.expires_at < datetime.utcnow():
        return False
    return True
