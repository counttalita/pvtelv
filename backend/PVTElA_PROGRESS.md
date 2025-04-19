# PVTElA MVP Progress Tracker

This document tracks the implementation of all registration and login flows, security, and session management for the PVTElA digital wallet MVP.

## Registration Flow

### 1. Initial Registration
- [x] E.164 phone validation
- [x] Disposable/VoIP check
- [x] Carrier/region restriction
- [x] Duplicate account check
- [x] OTP generation (mock Twilio), hash, expiry, limit
- [x] Device/network fingerprinting
- [x] Suspicious IP/device detection
- [x] CAPTCHA after repeated failures (stub)
- [x] Audit logging for registration events

### 2. Phone Verification
- [x] OTP comparison & expiry
- [x] Mark phone_verified
- [x] Exponential backoff
- [x] Profile creation & risk
- [x] Welcome notification/onboarding
- [ ] Welcome notification/onboarding

---


### 3. Additional Security
- [ ] IP/device validation
- [ ] CAPTCHA after failures
- [ ] Audit logging

## Login Flow

### 1. Initial Login
- [x] Phone/account status check
- [x] OTP for active accounts
- [x] Risk assessment

### 2. OTP Validation
- [x] Expiry check
- [x] Failed attempt lockout
- [x] last_login update
- [x] Session token (JWT)

### 3. Session Management
- [x] Sliding expiry
- [x] Multi-device/location tracking
- [x] Session revocation
- [x] Session validation helper/decorator for protected endpoints

---

## Change Log

- 2025-04-19: Project initialized, E.164 and duplicate check complete.
- 2025-04-19: KYC manual review via email, OTP logic fixes, registration duplicate check, and test alignment completed. All tests passing.

---

### Next Major Step
- [x] Implement robust KYC (Know Your Customer) process after login and before profile/welcome.
- [x] Profile creation and onboarding logic (after KYC)
    - [x] Welcome notification (in-app, email/SMS via Twilio)
    - [x] Intro tour step
    - [x] Security setup step
- [ ] Wallet/account setup (after onboarding)

**Legend:**
- [x] Complete
- [ ] Incomplete

---
