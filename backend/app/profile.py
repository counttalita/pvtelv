from app.db import db
from app.models import User
from datetime import datetime
from services.wallet_service import create_user_wallet # Added import

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
    
    # Create a wallet for the user
    try:
        wallet = create_user_wallet(user_id=profile.user_id)
        if not wallet:
            # Log an error or handle the case where wallet creation failed
            # For now, we'll just print a message, but in a real app, this needs robust handling
            print(f"Warning: Wallet creation failed for user_id {profile.user_id}")
    except Exception as e:
        # Log the exception
        print(f"Exception during wallet creation for user_id {profile.user_id}: {e}")
        # Depending on policy, you might want to rollback profile creation or queue wallet creation for retry

    trigger_onboarding(profile)
    return profile


def get_profile(user_id):
    return UserProfile.query.filter_by(user_id=user_id).first()


def trigger_onboarding(profile):
    # Send richer welcome: email, SMS, in-app
    from services.notification_service import send_sms, send_inapp # Removed send_email
    user = User.query.get(profile.user_id)
    # You may want to fetch user.email and user.phone if available
    welcome_msg = (
        f"Welcome to PVTElA, {profile.display_name or 'User'}!\n"
        "You're ready to start your digital wallet journey.\n"
        "Take our intro tour and set up security to get the most out of your account."
    )
    send_inapp(profile.user_id, welcome_msg)
    # Send email if email exists and is verified - REMOVED BLOCK
    # if user.email and user.email_verified: ... - REMOVED
    # Send SMS if phone is verified (user.phone is the primary ID and should exist)
    if user.phone_verified:
        send_sms(user.phone, welcome_msg)
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
