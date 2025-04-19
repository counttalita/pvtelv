from services.security_service import is_suspicious_ip, is_suspicious_device, should_show_captcha, track_registration

def test_ip_and_device_limits():
    ip = '1.2.3.4'
    device = 'abc123'
    # Register below limit
    for _ in range(5):
        track_registration(ip, device)
    assert not is_suspicious_ip(ip)
    assert not is_suspicious_device(device)
    # Register above limit
    for _ in range(2):
        track_registration(ip, device)
    assert is_suspicious_ip(ip)
    assert is_suspicious_device(device)

def test_captcha_trigger():
    assert not should_show_captcha(1)
    assert should_show_captcha(2)
    assert should_show_captcha(3)
