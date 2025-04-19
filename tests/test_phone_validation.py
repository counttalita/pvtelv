from services.phone_validation import is_disposable_or_voip, is_allowed_carrier_and_region

def test_disposable_voip_detection():
    assert is_disposable_or_voip('+99912345678')
    assert not is_disposable_or_voip('+14155552671')

def test_carrier_region_restriction():
    assert not is_allowed_carrier_and_region('+88812345678')
    assert is_allowed_carrier_and_region('+14155552671')
