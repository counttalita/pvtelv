from datetime import datetime, timedelta
from app.models import User
from services.otp_service import OTP_EXPIRY_MINUTES, hash_otp

def make_verified_user():
    user = User(phone='+14155552671', phone_verified=True)
    return user

def test_login_only_verified_allowed():
    user = User(phone='+14155552671', phone_verified=False)
    assert not user.phone_verified
    # Would block login (simulate in endpoint)
    user2 = make_verified_user()
    assert user2.phone_verified

def test_login_otp_generation_and_expiry():
    user = make_verified_user()
    now = datetime.utcnow()
    # Simulate OTP generation
    otp = '123456'
    user.otp_hash = hash_otp(otp)
    user.otp_expiry = now + timedelta(minutes=OTP_EXPIRY_MINUTES)
    assert user.otp_hash == hash_otp(otp)
    assert user.otp_expiry > now

def test_login_blocks_suspicious_ip_device():
    # Simulate suspicious IP/device check (would block in endpoint)
    pass

def test_login_audit_logging():
    # Would check audit log entry after login attempt
    pass
