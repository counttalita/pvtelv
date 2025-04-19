from functools import wraps
from flask import request, jsonify
from app.session import is_session_active
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

def require_session(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_jwt_from_request()
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        payload = decode_jwt(token)
        if not payload or not is_session_active(payload.get('jti')):
            return jsonify({'error': 'Invalid or expired session'}), 401
        request.user = payload
        return f(*args, **kwargs)
    return decorated
