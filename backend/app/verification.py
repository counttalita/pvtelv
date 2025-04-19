from flask import Blueprint, request, jsonify
from app.models import User, db
from services.otp_service import (
    hash_otp, is_otp_expired, can_attempt_otp_verification,
    record_failed_otp_verification, reset_otp_verification_failures
)
from datetime import datetime

verification_bp = Blueprint('verification', __name__)

@verification_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    phone = data.get('phone')
    otp = data.get('otp')
    if not phone or not otp:
        return jsonify({'error': 'Phone and OTP required'}), 400
    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    now = datetime.utcnow()
    allowed, wait = can_attempt_otp_verification(user, now)
    if not allowed:
        return jsonify({'error': f'Too many failed attempts. Wait {int(wait)} seconds.'}), 429
    if is_otp_expired(user, now):
        record_failed_otp_verification(user, now)
        db.session.commit()
        return jsonify({'error': 'OTP expired'}), 400
    if user.otp_hash != hash_otp(otp):
        record_failed_otp_verification(user, now)
        db.session.commit()
        return jsonify({'error': 'Invalid OTP'}), 400
    # Success: verify phone, reset failures
    user.phone_verified = True
    reset_otp_verification_failures(user)
    db.session.commit()
    return jsonify({'message': 'Phone verified successfully!'}), 200
