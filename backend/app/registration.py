from flask import Blueprint, request, jsonify

registration_bp = Blueprint('registration', __name__)

import phonenumbers

from .models import User, db

from services.phone_validation import is_disposable_or_voip, is_allowed_carrier_and_region

from services.otp_service import generate_otp, hash_otp, can_request_otp, record_otp_attempt, OTP_EXPIRY_MINUTES, is_user_locked_out

@registration_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    phone = data.get('phone')
    if not phone:
        return jsonify({'error': 'Phone number required'}), 400
    try:
        parsed = phonenumbers.parse(phone, None)
        if not phonenumbers.is_possible_number(parsed) or not phonenumbers.is_valid_number(parsed):
            raise ValueError()
    except Exception:
        return jsonify({'error': 'Invalid phone number format'}), 400
    if is_disposable_or_voip(phone):
        return jsonify({'error': 'Disposable or VoIP numbers are not allowed'}), 400
    if not is_allowed_carrier_and_region(phone):
        return jsonify({'error': 'Carrier or region not allowed'}), 400
    # Check for duplicate
    existing = User.query.filter_by(phone=phone).first()
    if existing:
        return jsonify({'error': 'Phone number already registered'}), 400
    else:
        from services.fingerprint_service import get_device_fingerprint, get_ip_address, get_location_from_ip
        user_agent = request.headers.get('User-Agent', '')
        ip = get_ip_address(request)
        location = get_location_from_ip(ip)
        user = User(
            phone=phone,
            device_fingerprint=get_device_fingerprint(user_agent),
            registration_ip=ip,
            registration_location=str(location) if location else None
        )
        db.session.add(user)
    # Security: suspicious IP/device and CAPTCHA
    from services.security_service import track_registration, is_suspicious_ip, is_suspicious_device, should_show_captcha
    from app.audit import log_audit
    ip = user.registration_ip
    device_fingerprint = user.device_fingerprint
    track_registration(ip, device_fingerprint)
    suspicious_ip = is_suspicious_ip(ip)
    suspicious_device = is_suspicious_device(device_fingerprint)
    captcha_required = should_show_captcha(user.failed_otp_attempts or 0)
    if suspicious_ip or suspicious_device:
        log_audit('registration', phone, ip, device_fingerprint, 'blocked', details='Suspicious IP or device')
        return jsonify({'error': 'Suspicious activity detected. Registration blocked.'}), 403
    if captcha_required:
        log_audit('registration', phone, ip, device_fingerprint, 'captcha', details='CAPTCHA required')
        return jsonify({'error': 'Please complete CAPTCHA to continue.'}), 403
    # OTP limiting and lockout
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    if is_user_locked_out(user, now):
        log_audit('registration', phone, ip, device_fingerprint, 'locked', details='OTP lockout')
        return jsonify({'error': 'Too many OTP requests. Try again later.'}), 429
    if not can_request_otp(user, now):
        log_audit('registration', phone, ip, device_fingerprint, 'rate_limited', details='OTP request limit')
        return jsonify({'error': 'OTP request limit reached. Try again later.'}), 429
    # Generate and store OTP
    otp = generate_otp()
    user.otp_hash = hash_otp(otp)
    user.otp_expiry = now + timedelta(minutes=OTP_EXPIRY_MINUTES)
    record_otp_attempt(user, now)
    db.session.commit()
    log_audit('registration', phone, ip, device_fingerprint, 'success', details='OTP sent')
    # Send OTP via Twilio (mock for now)
    print(f"[MOCK] Sending OTP {otp} to {phone}")
    return jsonify({'message': 'OTP sent to phone.'}), 200
