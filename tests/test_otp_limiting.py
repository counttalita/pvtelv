from datetime import datetime, timedelta
from app.models import User
from services.otp_service import (
    OTP_ATTEMPT_LIMIT, OTP_LOCKOUT_MINUTES, OTP_EXPIRY_MINUTES,
    can_request_otp, record_otp_attempt, is_user_locked_out, is_otp_expired
)

# Mocks for User model fields

def make_user():
    return User(phone='+14155552671')

def test_otp_attempt_limit_and_lockout():
    user = make_user()
    now = datetime.utcnow()
    user.otp_last_requested = now - timedelta(minutes=1)
    user.otp_attempts = OTP_ATTEMPT_LIMIT - 1
    user.otp_lockout_until = None
    assert can_request_otp(user, now)
    record_otp_attempt(user, now)
    assert user.otp_attempts == OTP_ATTEMPT_LIMIT
    assert user.otp_lockout_until is not None
    assert is_user_locked_out(user, now)

def test_otp_lockout_expires():
    user = make_user()
    now = datetime.utcnow()
    user.otp_lockout_until = now - timedelta(minutes=1)
    assert not is_user_locked_out(user, now)

def test_otp_expiry():
    user = make_user()
    now = datetime.utcnow()
    user.otp_expiry = now - timedelta(minutes=1)
    assert is_otp_expired(user, now)
    user.otp_expiry = now + timedelta(minutes=4)
    assert not is_otp_expired(user, now)
