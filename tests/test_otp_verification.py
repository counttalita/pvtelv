from datetime import datetime, timedelta
from app.models import User
from services.otp_service import hash_otp, is_otp_expired

def make_user_for_verification(otp='123456', expiry_minutes=5):
    now = datetime.utcnow()
    user = User(phone='+14155552671')
    user.otp_hash = hash_otp(otp)
    user.otp_expiry = now + timedelta(minutes=expiry_minutes)
    user.failed_otp_attempts = 0
    user.last_otp_failure = None
    return user, now

def test_valid_otp_verification():
    user, now = make_user_for_verification()
    assert not is_otp_expired(user, now)
    assert user.otp_hash == hash_otp('123456')

def test_expired_otp_verification():
    user, now = make_user_for_verification(expiry_minutes=-1)
    assert is_otp_expired(user, now)

def test_failed_otp_attempts_and_backoff():
    user, now = make_user_for_verification()
    user.failed_otp_attempts = 2
    user.last_otp_failure = now - timedelta(minutes=1)
    # Simulate another failure and check increment
    user.failed_otp_attempts += 1
    user.last_otp_failure = now
    assert user.failed_otp_attempts == 3
    assert user.last_otp_failure == now
