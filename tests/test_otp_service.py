from services.otp_service import generate_otp, hash_otp, OTP_LENGTH
import re

def test_generate_otp_length_and_digits():
    otp = generate_otp()
    assert len(otp) == OTP_LENGTH
    assert re.match(r'^\d{' + str(OTP_LENGTH) + r'}$', otp)

def test_hash_otp_consistency():
    otp = '123456'
    h1 = hash_otp(otp)
    h2 = hash_otp(otp)
    assert h1 == h2
    assert len(h1) == 64  # sha256 hex
