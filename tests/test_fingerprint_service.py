from services.fingerprint_service import get_device_fingerprint, get_ip_address, get_location_from_ip

class DummyRequest:
    def __init__(self, headers=None, remote_addr=None):
        self.headers = headers or {}
        self.remote_addr = remote_addr

def test_get_device_fingerprint():
    ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
    fp = get_device_fingerprint(ua)
    assert isinstance(fp, str) and len(fp) == 64
    assert fp == get_device_fingerprint(ua)

def test_get_ip_address_basic():
    req = DummyRequest(remote_addr='1.2.3.4')
    assert get_ip_address(req) == '1.2.3.4'

def test_get_ip_address_forwarded():
    req = DummyRequest(headers={'X-Forwarded-For': '5.6.7.8, 9.9.9.9'}, remote_addr='1.2.3.4')
    assert get_ip_address(req) == '5.6.7.8'

def test_get_location_from_ip():
    assert get_location_from_ip('127.0.0.1')['country'] == 'Local'
    assert get_location_from_ip('8.8.8.8') is None
