import hashlib

def get_device_fingerprint(user_agent: str) -> str:
    # Simple hash of user agent for demo; use a real fingerprinting lib in prod
    return hashlib.sha256(user_agent.encode()).hexdigest() if user_agent else None

def get_ip_address(request) -> str:
    # Handles X-Forwarded-For if behind proxy
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    return request.remote_addr

def get_location_from_ip(ip: str) -> dict:
    # Placeholder: In production, use a geoip service
    # For demo, return None or a fake location
    if ip and ip.startswith('127.'):
        return {'country': 'Local', 'city': 'Localhost'}
    return None
