import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_registration_valid_phone(client):
    # E.164 valid example: +14155552671
    response = client.post('/register', json={'phone': '+14155552671'})
    assert response.status_code == 200
    assert 'OTP sent to phone.' in response.get_json()['message']

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
