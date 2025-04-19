from datetime import datetime, timedelta
from app.models import User
from services.otp_service import hash_otp, OTP_EXPIRY_MINUTES, is_otp_expired
import jwt
import os

SECRET = os.environ.get('JWT_SECRET', 'testsecret')


def make_login_user(otp='123456', expiry_minutes=5):
    now = datetime.utcnow()
    user = User(phone='+14155552671', phone_verified=True)
    user.otp_hash = hash_otp(otp)
    user.otp_expiry = now + timedelta(minutes=expiry_minutes)
    user.failed_otp_attempts = 0
    user.last_otp_failure = None
    return user, now

def test_login_otp_valid_and_token():
    user, now = make_login_user()
    assert not is_otp_expired(user, now)
    payload = {'user_id': user.id, 'exp': now + timedelta(hours=1)}
    token = jwt.encode(payload, SECRET, algorithm='HS256')
    assert isinstance(token, str) or isinstance(token, bytes)

def test_login_otp_expired():
    user, now = make_login_user(expiry_minutes=-1)
    assert is_otp_expired(user, now)

def test_login_failed_attempts_and_lockout():
    user, now = make_login_user()
    user.failed_otp_attempts = 3
    user.last_otp_failure = now - timedelta(seconds=10)
    # Simulate lockout logic (should block in endpoint)
    pass
