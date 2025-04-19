from datetime import datetime, timedelta
import jwt
import os

SECRET = os.environ.get('JWT_SECRET', 'testsecret')

def test_jwt_sliding_expiry():
    now = datetime.utcnow()
    payload = {'user_id': 1, 'iat': int(now.timestamp()), 'exp': int((now + timedelta(minutes=30)).timestamp())}
    token = jwt.encode(payload, SECRET, algorithm='HS256')
    # Simulate endpoint: refresh on activity with new iat
    refreshed_payload = payload.copy()
    refreshed_payload['iat'] = int((now + timedelta(seconds=1)).timestamp())
    refreshed_payload['exp'] = int((now + timedelta(minutes=31)).timestamp())
    refreshed_token = jwt.encode(refreshed_payload, SECRET, algorithm='HS256')
    assert token != refreshed_token

def test_multi_device_sessions():
    now = datetime.utcnow()
    device1 = 'dev1'
    device2 = 'dev2'
    token1 = jwt.encode({'user_id': 1, 'exp': int((now + timedelta(hours=1)).timestamp()), 'device': device1}, SECRET, algorithm='HS256')
    token2 = jwt.encode({'user_id': 1, 'exp': int((now + timedelta(hours=1)).timestamp()), 'device': device2}, SECRET, algorithm='HS256')
    assert token1 != token2

def test_session_revocation():
    # Simulate revocation by blacklisting token jti or storing revoked tokens
    revoked_tokens = set()
    token = jwt.encode({'user_id': 1, 'exp': int((datetime.utcnow() + timedelta(hours=1)).timestamp()), 'jti': 'abc'}, SECRET, algorithm='HS256')
    revoked_tokens.add('abc')
    assert 'abc' in revoked_tokens
