from flask import Blueprint, request, jsonify
from services.session_helper import require_session
from app.profile import create_profile, get_profile
from services.kyc_service import get_kyc_status

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['POST'])
@require_session
def create_user_profile():
    user_id = request.user['user_id']
    # Check KYC status
    status, _ = get_kyc_status(user_id)
    if status != 'approved':
        return jsonify({'error': 'KYC approval required'}), 403
    display_name = request.json.get('display_name')
    profile = create_profile(user_id, display_name)
    return jsonify({'message': 'Profile created', 'profile_id': profile.id}), 201

@profile_bp.route('/profile', methods=['GET'])
@require_session
def get_user_profile():
    user_id = request.user['user_id']
    profile = get_profile(user_id)
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    return jsonify({
        'profile_id': profile.id,
        'user_id': profile.user_id,
        'display_name': profile.display_name,
        'created_at': profile.created_at.isoformat(),
        'welcome_sent': profile.welcome_sent,
        'onboarding_completed': profile.onboarding_completed,
        'preferences': profile.preferences
    }), 200

@profile_bp.route('/profile/preferences', methods=['POST'])
@require_session
def update_user_preferences():
    user_id = request.user['user_id']
    prefs = request.json.get('preferences')
    if not isinstance(prefs, dict):
        return jsonify({'error': 'Invalid preferences'}), 400
    ok = update_preferences(user_id, prefs)
    if not ok:
        return jsonify({'error': 'Profile not found'}), 404
    return jsonify({'message': 'Preferences updated'}), 200

@profile_bp.route('/profile/onboarding-complete', methods=['POST'])
@require_session
def complete_onboarding():
    user_id = request.user['user_id']
    ok = mark_onboarding_complete(user_id)
    if not ok:
        return jsonify({'error': 'Profile not found'}), 404
    return jsonify({'message': 'Onboarding marked as complete'}), 200
