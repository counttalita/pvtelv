from flask import Blueprint, request, jsonify
from app.models import User, db
from services.otp_service import generate_otp, hash_otp, OTP_EXPIRY_MINUTES, can_request_otp, record_otp_attempt, is_user_locked_out
from services.fingerprint_service import get_device_fingerprint, get_ip_address
from services.security_service import track_registration, is_suspicious_ip, is_suspicious_device, should_show_captcha
from app.audit import log_audit
from datetime import datetime, timedelta

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    phone = data.get('phone')
    if not phone:
        return jsonify({'error': 'Phone number required'}), 400
    user = User.query.filter_by(phone=phone).first()
    ip = get_ip_address(request)
    user_agent = request.headers.get('User-Agent', '')
    device_fingerprint = get_device_fingerprint(user_agent)
    if not user:
        log_audit('login', phone, ip, device_fingerprint, 'fail', details='No such user')
        return jsonify({'error': 'User not found'}), 404
    if not user.phone_verified:
        log_audit('login', phone, ip, device_fingerprint, 'fail', details='Phone not verified')
        return jsonify({'error': 'Phone not verified'}), 403
    # Security: suspicious IP/device and CAPTCHA
    track_registration(ip, device_fingerprint)
    if is_suspicious_ip(ip) or is_suspicious_device(device_fingerprint):
        log_audit('login', phone, ip, device_fingerprint, 'blocked', details='Suspicious IP or device')
        return jsonify({'error': 'Suspicious activity detected. Login blocked.'}), 403
    if should_show_captcha(user.failed_otp_attempts or 0):
        log_audit('login', phone, ip, device_fingerprint, 'captcha', details='CAPTCHA required')
        return jsonify({'error': 'Please complete CAPTCHA to continue.'}), 403
    # OTP limiting and lockout
    now = datetime.utcnow()
    if is_user_locked_out(user, now):
        log_audit('login', phone, ip, device_fingerprint, 'locked', details='OTP lockout')
        return jsonify({'error': 'Too many OTP requests. Try again later.'}), 429
    if not can_request_otp(user, now):
        log_audit('login', phone, ip, device_fingerprint, 'rate_limited', details='OTP request limit')
        return jsonify({'error': 'OTP request limit reached. Try again later.'}), 429
    # Generate and store OTP
    otp = generate_otp()
    user.otp_hash = hash_otp(otp)
    user.otp_expiry = now + timedelta(minutes=OTP_EXPIRY_MINUTES)
    record_otp_attempt(user, now)
    db.session.commit()
    log_audit('login', phone, ip, device_fingerprint, 'success', details='OTP sent')
    # Send OTP via Twilio (mock for now)
    print(f"[MOCK] Sending OTP {otp} to {phone}")
    return jsonify({'message': 'OTP sent to phone.'}), 200

@login_bp.route('/verify-login-otp', methods=['POST'])
def verify_login_otp():
    import jwt
    import os
    import uuid
    from app.session import create_session
    data = request.get_json()
    phone = data.get('phone')
    otp = data.get('otp')
    if not phone or not otp:
        return jsonify({'error': 'Phone and OTP required'}), 400
    user = User.query.filter_by(phone=phone).first()
    ip = get_ip_address(request)
    user_agent = request.headers.get('User-Agent', '')
    device_fingerprint = get_device_fingerprint(user_agent)
    if not user:
        log_audit('login_otp', phone, ip, device_fingerprint, 'fail', details='No such user')
        return jsonify({'error': 'User not found'}), 404
    from services.otp_service import is_otp_expired, can_attempt_otp_verification, record_failed_otp_verification, reset_otp_verification_failures
    now = datetime.utcnow()
    allowed, wait = can_attempt_otp_verification(user, now)
    if not allowed:
        log_audit('login_otp', phone, ip, device_fingerprint, 'locked', details=f'Backoff: wait {int(wait)}s')
        return jsonify({'error': f'Too many failed attempts. Wait {int(wait)} seconds.'}), 429
    if is_otp_expired(user, now):
        record_failed_otp_verification(user, now)
        db.session.commit()
        log_audit('login_otp', phone, ip, device_fingerprint, 'fail', details='OTP expired')
        return jsonify({'error': 'OTP expired'}), 400
    if user.otp_hash != hash_otp(otp):
        record_failed_otp_verification(user, now)
        db.session.commit()
        log_audit('login_otp', phone, ip, device_fingerprint, 'fail', details='Invalid OTP')
        return jsonify({'error': 'Invalid OTP'}), 400
    # Success: update last_login, reset failures, issue JWT & session
    user.last_login = now
    reset_otp_verification_failures(user)
    db.session.commit()
    jti = str(uuid.uuid4())
    exp = now + timedelta(hours=1)
    payload = {
        'user_id': user.id,
        'phone': user.phone,
        'iat': int(now.timestamp()),
        'exp': int(exp.timestamp()),
        'device': device_fingerprint,
        'jti': jti
    }
    secret = os.environ.get('JWT_SECRET', 'testsecret')
    token = jwt.encode(payload, secret, algorithm='HS256')
    create_session(user.id, device_fingerprint, jti, exp)
    log_audit('login_otp', phone, ip, device_fingerprint, 'success', details='Login successful')
    return jsonify({'message': 'Login successful', 'token': token}), 200

from app.session import is_session_active, refresh_session, revoke_session
import jwt
import os

def get_jwt_from_request():
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth.split(' ', 1)[1]
    return None

def decode_jwt(token):
    secret = os.environ.get('JWT_SECRET', 'testsecret')
    try:
        return jwt.decode(token, secret, algorithms=['HS256'])
    except Exception:
        return None

@login_bp.route('/refresh-session', methods=['POST'])
def refresh_session_endpoint():
    token = get_jwt_from_request()
    if not token:
        return jsonify({'error': 'Missing token'}), 401
    payload = decode_jwt(token)
    if not payload or not is_session_active(payload.get('jti')):
        return jsonify({'error': 'Invalid or expired session'}), 401
    new_exp = datetime.utcnow() + timedelta(hours=1)
    if not refresh_session(payload['jti'], new_exp):
        return jsonify({'error': 'Could not refresh session'}), 400
    payload['exp'] = int(new_exp.timestamp())
    secret = os.environ.get('JWT_SECRET', 'testsecret')
    new_token = jwt.encode(payload, secret, algorithm='HS256')
    return jsonify({'token': new_token}), 200

@login_bp.route('/logout', methods=['POST'])
def logout():
    token = get_jwt_from_request()
    if not token:
        return jsonify({'error': 'Missing token'}), 401
    payload = decode_jwt(token)
    if not payload:
        return jsonify({'error': 'Invalid token'}), 401
    if not revoke_session(payload['jti']):
        return jsonify({'error': 'Could not revoke session'}), 400
    return jsonify({'message': 'Logged out successfully'}), 200
