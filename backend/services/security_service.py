from datetime import datetime, timedelta

# Simple in-memory IP/device registration tracker for demo (replace with DB/cache in prod)
_ip_register_times = {}
_device_register_times = {}

IP_LIMIT = 5  # max registrations per IP per hour
DEVICE_LIMIT = 5  # max registrations per device per hour
CAPTCHA_AFTER = 2  # trigger CAPTCHA after this many failed attempts


def track_registration(ip, device_fingerprint):
    now = datetime.utcnow()
    _ip_register_times.setdefault(ip, []).append(now)
    _device_register_times.setdefault(device_fingerprint, []).append(now)


def is_suspicious_ip(ip):
    now = datetime.utcnow()
    recent = [t for t in _ip_register_times.get(ip, []) if (now - t) < timedelta(hours=1)]
    return len(recent) > IP_LIMIT


def is_suspicious_device(device_fingerprint):
    now = datetime.utcnow()
    recent = [t for t in _device_register_times.get(device_fingerprint, []) if (now - t) < timedelta(hours=1)]
    return len(recent) > DEVICE_LIMIT


def should_show_captcha(failed_attempts):
    return failed_attempts >= CAPTCHA_AFTER
