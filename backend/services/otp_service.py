import hashlib
import random
from datetime import datetime, timedelta

OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 5
OTP_ATTEMPT_LIMIT = 3
OTP_LOCKOUT_MINUTES = 15

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(OTP_LENGTH)])

def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()

from datetime import datetime, timedelta

# ... (existing code)

def can_request_otp(user, now=None):
    now = now or datetime.utcnow()
    # If locked out
    if user.otp_lockout_until and user.otp_lockout_until > now:
        return False
    # If attempts exceeded within 15 minutes
    attempts = user.otp_attempts or 0
    if attempts >= OTP_ATTEMPT_LIMIT:
        if user.otp_last_requested and (now - user.otp_last_requested) < timedelta(minutes=OTP_LOCKOUT_MINUTES):
            user.otp_lockout_until = now + timedelta(minutes=OTP_LOCKOUT_MINUTES)
            return False
        else:
            user.otp_attempts = 0
    return True

def record_otp_attempt(user, now=None):
    now = now or datetime.utcnow()
    user.otp_attempts = (user.otp_attempts or 0) + 1
    user.otp_last_requested = now
    if user.otp_attempts >= OTP_ATTEMPT_LIMIT:
        user.otp_lockout_until = now + timedelta(minutes=OTP_LOCKOUT_MINUTES)

def is_user_locked_out(user, now=None):
    now = now or datetime.utcnow()
    return bool(user.otp_lockout_until and user.otp_lockout_until > now)

def is_otp_expired(user, now=None):
    now = now or datetime.utcnow()
    return not user.otp_expiry or user.otp_expiry < now

# Exponential backoff for failed OTP verification
BACKOFF_BASE_SECONDS = 30
BACKOFF_MAX_ATTEMPTS = 5
BACKOFF_MULTIPLIER = 2

def get_backoff_seconds(attempts):
    if attempts <= 0:
        return 0
    return min(BACKOFF_BASE_SECONDS * (BACKOFF_MULTIPLIER ** (attempts-1)), 15*60)  # max 15min

def can_attempt_otp_verification(user, now=None):
    now = now or datetime.utcnow()
    if user.failed_otp_attempts and user.last_otp_failure:
        wait = get_backoff_seconds(user.failed_otp_attempts)
        if (now - user.last_otp_failure).total_seconds() < wait:
            return False, wait - (now - user.last_otp_failure).total_seconds()
    return True, 0

def record_failed_otp_verification(user, now=None):
    now = now or datetime.utcnow()
    user.failed_otp_attempts = (user.failed_otp_attempts or 0) + 1
    user.last_otp_failure = now

def reset_otp_verification_failures(user):
    user.failed_otp_attempts = 0
    user.last_otp_failure = None
