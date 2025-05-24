import pytest
from unittest.mock import patch # Retain patch if other things need mocking, or remove if not.
from datetime import datetime, timedelta
# Removed: from flask import current_app, url_for

from app import create_app
from app.models import User, db
from services.otp_service import hash_otp, is_otp_expired, generate_otp
# Removed: from app.verification import generate_email_verification_token, verify_email_verification_token


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    # app.config['SERVER_NAME'] = 'localhost.test' # Removed, not needed without url_for for email
    with app.app_context():
        db.drop_all()
        db.create_all()
    with app.test_client() as client:
        yield client

def _register_user_direct_db(phone, phone_verified=False): # Removed email related params
    """Helper to create a user directly in DB for testing OTP verification."""
    user = User(phone=phone, phone_verified=phone_verified, email=None) # Email is always None
    # Simulate OTP generation
    otp = generate_otp()
    user.otp_hash = hash_otp(otp)
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=10) # Ensure OTP is valid
    db.session.add(user)
    db.session.commit()
    return user, otp

def make_user_for_verification(otp='123456', expiry_minutes=5):
    # This function might be less used if we use _register_user_direct_db for endpoint tests
    now = datetime.utcnow()
    user = User(phone='+14155552671') # Default phone
    user.otp_hash = hash_otp(otp) # Hash the provided OTP
    user.otp_expiry = now + timedelta(minutes=expiry_minutes)
    user.failed_otp_attempts = 0
    user.last_otp_failure = None
    # For this helper, we might need to add it to a session if it's to be used by DB queries.
    return user, now

# --- Tests for OTP Verification Endpoint ---

# Basic success test for OTP verification endpoint
def test_otp_verify_success(client):
    phone = '+12345678901'
    with client.application.app_context():
        user, otp_value = _register_user_direct_db(phone, phone_verified=False)

    response = client.post('/verify-otp', json={'phone': phone, 'otp': otp_value})

    assert response.status_code == 200
    assert response.get_json()['message'] == 'Phone verified successfully!'

    with client.application.app_context():
        db_user = User.query.filter_by(phone=phone).first()
        assert db_user is not None
        assert db_user.phone_verified is True
        assert db_user.email is None # Ensure email is not set
        assert db_user.email_verified is False # Email verified should remain False

def test_otp_verify_invalid_otp(client):
    phone = '+12345678902'
    with client.application.app_context():
        user, _ = _register_user_direct_db(phone) # Real OTP is not 'wrong_otp'

    response = client.post('/verify-otp', json={'phone': phone, 'otp': 'wrong_otp'})
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Invalid OTP'
    with client.application.app_context():
        db_user = User.query.filter_by(phone=phone).first()
        assert db_user.phone_verified is False # Should still be false

def test_otp_verify_user_not_found(client):
    response = client.post('/verify-otp', json={'phone': '+19999999999', 'otp': '123456'})
    assert response.status_code == 404
    assert response.get_json()['error'] == 'User not found'

# Existing tests for OTP expiry, attempts, backoff can remain if they are service-level unit tests
# or can be adapted for endpoint testing if desired.
# The `make_user_for_verification` helper and its tests are more for unit-testing OTP logic.
# For endpoint tests, `_register_user_direct_db` and actual client calls are more relevant.

# Example of adapting one of the existing tests (if they were for OTP logic directly)
# This test is more of a unit test for the is_otp_expired service logic
def test_otp_service_expired_otp_logic(): # Renamed to clarify it's a service logic test
    user, now = make_user_for_verification(expiry_minutes=-1) # OTP generated in the past
    assert is_otp_expired(user, now) is True

def test_otp_service_valid_otp_logic(): # Renamed
    user, now = make_user_for_verification(otp='654321', expiry_minutes=5)
    assert is_otp_expired(user, now) is False
    assert user.otp_hash == hash_otp('654321') # Check hashing works as expected

# The email-related tests (test_otp_verify_sends_verification_email, etc.) are removed.
