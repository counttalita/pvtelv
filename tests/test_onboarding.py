import pytest
from app import create_app, db
from app.profile import create_profile, get_profile, update_preferences, mark_onboarding_complete
from flask import json

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_profile_creation_triggers_onboarding():
    from app import create_app
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        user_id = 123
        profile = create_profile(user_id, display_name="Test User")
        assert profile.welcome_sent is True
        assert profile.onboarding_completed is False
        assert profile.intro_tour_complete is False
        assert profile.security_setup_complete is False


def test_update_preferences():
    from app import create_app
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        user_id = 124
        create_profile(user_id, display_name="Prefs User")
        ok = update_preferences(user_id, {"currency": "ZAR", "theme": "dark"})
        assert ok
        profile = get_profile(user_id)
        assert 'currency' in profile.preferences


def test_mark_onboarding_complete():
    from app import create_app
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        user_id = 125
        create_profile(user_id, display_name="Onboard User")
        ok = mark_onboarding_complete(user_id)
        assert ok
        profile = get_profile(user_id)
        assert profile.onboarding_completed is True
