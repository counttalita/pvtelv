import pytest
from app import create_app
from app.models import User, db  # Added User and db
from flask import current_app # To access app context for db operations if needed outside client calls

# Keep the existing client fixture
@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    # Ensure database is clean for each test
    with app.app_context():
        db.drop_all()
        db.create_all()
    with app.test_client() as client:
        yield client

def test_registration_valid_phone(client):
    # E.164 valid example: +14155552671
    response = client.post('/register', json={'phone': '+14155552671'})
    assert response.status_code == 200
    assert 'OTP sent to phone.' in response.get_json()['message']
    
    # Verify user in DB
    with client.application.app_context():
        user = User.query.filter_by(phone='+14155552671').first()
        assert user is not None
        assert user.email is None # Email should always be None now

    # Try to register the same phone again
    response2 = client.post('/register', json={'phone': '+14155552671'})
    assert response2.status_code == 400
    assert response2.get_json()['error'] == 'Phone number already registered'

def test_registration_invalid_phone(client):
    # Not E.164
    response = client.post('/register', json={'phone': '12345'})
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Invalid phone number format'

def test_registration_missing_phone(client):
    response = client.post('/register', json={})
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Phone number required'

# --- Email Registration Tests Removed ---
# test_registration_with_valid_email removed
# test_registration_with_invalid_email_format removed
# test_registration_with_existing_email removed

# test_registration_without_email can be kept and serves as the standard test now
def test_registration_standard(client): # Renamed from test_registration_without_email
    phone = '+14155550005'
    response = client.post('/register', json={'phone': phone}) # No email field in payload
    assert response.status_code == 200
    assert 'OTP sent to phone.' in response.get_json()['message']

    with client.application.app_context():
        user = User.query.filter_by(phone=phone).first()
        assert user is not None
        assert user.email is None # Email should be None
        assert user.email_verified is False # Default is False, and remains so
