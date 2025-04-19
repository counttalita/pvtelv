from services.kyc_service import submit_kyc, get_kyc_status, review_kyc
from app.models import db

class DummyUser:
    id = 1

def test_kyc_submission_and_status():
    from app import create_app
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = DummyUser()
        documents = '{"id_card": "file1.jpg", "selfie": "file2.jpg"}'
        sub = submit_kyc(user.id, documents)
        assert sub.user_id == user.id
        status, sub2 = get_kyc_status(user.id)
        assert status == 'pending_manual'
        assert sub2.documents == documents

def test_kyc_review():
    from app import create_app
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = DummyUser()
        documents = '{"id_card": "file1.jpg", "selfie": "file2.jpg"}'
        sub = submit_kyc(user.id, documents)
        ok = review_kyc(sub.id, 'approved', notes='Looks good')
        assert ok
        status, reviewed = get_kyc_status(user.id)
        assert status == 'approved'
        assert reviewed.notes == 'Looks good'
