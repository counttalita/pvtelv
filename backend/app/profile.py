from app.db import db
from app.models import User
from datetime import datetime

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    display_name = db.Column(db.String(64), nullable=True)
    # Onboarding fields
    welcome_sent = db.Column(db.Boolean, default=False)
    onboarding_completed = db.Column(db.Boolean, default=False)
    preferences = db.Column(db.Text, nullable=True)  # JSON string for user prefs
    intro_tour_complete = db.Column(db.Boolean, default=False)
    security_setup_complete = db.Column(db.Boolean, default=False)
    # Add more profile fields as needed (e.g., avatar, bio, address, etc.)


def create_profile(user_id, display_name=None):
    profile = UserProfile(user_id=user_id, display_name=display_name)
    db.session.add(profile)
    db.session.commit()
    trigger_onboarding(profile)
    return profile


def get_profile(user_id):
    return UserProfile.query.filter_by(user_id=user_id).first()


def trigger_onboarding(profile):
    # Send richer welcome: email, SMS, in-app
    from services.notification_service import send_email, send_sms, send_inapp
    user = User.query.get(profile.user_id)
    # You may want to fetch user.email and user.phone if available
    welcome_msg = (
        f"Welcome to PVTElA, {profile.display_name or 'User'}!\n"
        "You're ready to start your digital wallet journey.\n"
        "Take our intro tour and set up security to get the most out of your account."
    )
    send_inapp(profile.user_id, welcome_msg)
    # Uncomment if user.email/user.phone fields exist:
    # if user.email: send_email(user.email, 'Welcome to PVTElA', welcome_msg)
    # if user.phone: send_sms(user.phone, welcome_msg)
    profile.welcome_sent = True
    db.session.commit()
    print(f"Welcome notification sent to user_id {profile.user_id}")


def update_preferences(user_id, preferences):
    import json
    profile = get_profile(user_id)
    if profile:
        profile.preferences = json.dumps(preferences)
        db.session.commit()
        return True
    return False


def mark_onboarding_complete(user_id):
    profile = get_profile(user_id)
    if profile:
        profile.onboarding_completed = True
        db.session.commit()
        return True
    return False
