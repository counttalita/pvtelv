import pytest
from unittest.mock import patch
from flask import jsonify # For creating response contexts if needed, or just use client
from app import create_app, db # db from app, not app.models
from app.models import User # Assuming User model is needed for creating test users
from app.kyc import KYCSubmission # To create KYCSubmission instances for testing
from services.kyc_service import submit_kyc, get_kyc_status, review_kyc # Keep service calls for setup if needed

# Fixture for the Flask test client
@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key' # For session handling
    
    with app.app_context():
        db.drop_all()
        db.create_all()
    
    with app.test_client() as client:
        yield client

# Fixture to create a test user
@pytest.fixture
def test_user(client): # client fixture provides app_context
    user = User(phone="+11234567890", phone_verified=True) # Add required fields for User
    db.session.add(user)
    db.session.commit()
    return user

# Helper to simulate a logged-in user session for the @require_session decorator
# This depends on how @require_session actually works.
# If it checks flask.session, we modify that. If it checks g.user, we patch that.
# For this example, let's assume @require_session sets request.user based on a session cookie.
# A more direct way for testing is to patch the decorator or what it relies on.
# For now, we'll patch where `request.user` would be accessed or the decorator itself.

def test_kyc_status_endpoint_with_submission(client, test_user):
    documents_json = '{"id_card": "file1.jpg", "selfie": "file2.jpg"}'
    # Create a KYC submission directly via service for setup
    with client.application.app_context():
        submission = submit_kyc(user_id=test_user.id, documents=documents_json)
        assert submission is not None
        submission_id = submission.id # Get the ID for verification

    # Mock the session or user loading part of @require_session
    # Assuming require_session populates request.user
    mock_user_payload = {'user_id': test_user.id, 'role': 'user'}

    with patch('services.session_helper.validate_session_token') as mock_validate_token:
        # Simulate that validate_session_token returns a valid user payload
        # The exact return structure depends on your validate_session_token
        mock_validate_token.return_value = mock_user_payload 
        
        # Make request to the endpoint
        response = client.get('/kyc/status') # Ensure your app registers kyc_bp without /api prefix or adjust URL

    assert response.status_code == 200
    json_data = response.get_json()
    
    assert json_data['id'] == submission_id
    assert json_data['user_id'] == test_user.id
    assert json_data['status'] == 'pending_manual' # Default status from model
    assert json_data['documents'] == documents_json
    assert json_data['reviewed_at'] is None
    assert json_data['notes'] is None
    assert 'submitted_at' in json_data

def test_kyc_status_endpoint_no_submission(client, test_user):
    # Mock the session or user loading
    mock_user_payload = {'user_id': test_user.id, 'role': 'user'}
    with patch('services.session_helper.validate_session_token') as mock_validate_token:
        mock_validate_token.return_value = mock_user_payload
        
        # Ensure no KYC submission exists for this user (handled by clean DB from fixture)
        response = client.get('/kyc/status')

    assert response.status_code == 200
    json_data = response.get_json()
    
    # Based on the refactored route:
    # if sub is None: return jsonify({'status': status, 'message': 'No KYC submission found.'}), 200
    # The `get_kyc_status` service likely returns 'not_started' or similar for `status`.
    assert json_data['status'] == 'not_started' # Assuming this is what get_kyc_status returns
    assert 'message' in json_data
    assert json_data['message'] == 'No KYC submission found.'


# Keep existing service-level tests if they are still valuable for unit testing logic
# For example, test_kyc_review might still be useful for testing the review_kyc service function directly.
# However, ensure they don't conflict with endpoint tests (e.g. by using different users or cleaning up)

def test_kyc_review_service_logic(): # Renamed to clarify it's testing service logic
    from app import create_app # Local import to avoid issues if app is not always available globally
    app = create_app()
    with app.app_context():
        db.drop_all() # Ensure clean state for this specific test if needed
        db.create_all()
        
        # Create a dummy user directly for this test as it's not using the client
        user = User(phone="+19876543210", phone_verified=True)
        db.session.add(user)
        db.session.commit()

        documents = '{"id_card": "file_review.jpg"}'
        sub = submit_kyc(user.id, documents)
        assert sub is not None
        
        ok = review_kyc(sub.id, 'approved', notes='Service test: Looks good')
        assert ok
        
        status, reviewed_submission = get_kyc_status(user.id)
        assert status == 'approved'
        assert reviewed_submission is not None
        assert reviewed_submission.notes == 'Service test: Looks good'
        assert reviewed_submission.reviewed_at is not None
