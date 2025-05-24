# PVTElA MVP Progress Tracker

This document tracks the implementation of all registration and login flows, security, and session management for the PVTElA digital wallet MVP.

## Registration Flow

### 1. Initial Registration
- [x] E.164 phone validation
- [x] Disposable/VoIP check
- [x] Carrier/region restriction
- [x] Duplicate account check
- [x] OTP generation (Twilio integration is MOCKED), hash, expiry, limit
- [x] Device/network fingerprinting
- [x] Suspicious IP/device detection
- [x] CAPTCHA after repeated failures (CAPTCHA threshold logging implemented; full CAPTCHA deferred).
- [x] Audit logging for registration events

### 2. Phone Verification
- [x] OTP comparison & expiry
- [x] Mark phone_verified
- [x] Exponential backoff
- [x] Profile creation & risk
- [x] Welcome notification/onboarding (in-app, SMS; user emails removed from this flow).

---


### 3. Additional Security
- [~] IP/device validation (basic in-memory tracking implemented, further enhancements can be future work)
- [x] CAPTCHA after repeated failures (CAPTCHA threshold logging implemented; full CAPTCHA deferred).

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

### Implemented Wallet Management Features
- [x] Implement robust KYC (Know Your Customer) process after login and before profile/welcome.
- [x] Profile creation and onboarding logic (after KYC)
    - [x] Welcome notification (in-app, SMS; user emails removed from this flow).
    - [x] Intro tour step
    - [x] Security setup step
- [x] **Implement Wallet Management Features**
    - [x] Wallet Model & Core Logic (balance, user association)
    - [x] Transaction Model & Logging (deposits, withdrawals, fees)
    - [x] PayPal Integration for Deposits (Top-Up with 15% fee)
    - [x] Withdrawal Functionality (Bank & PayPal, with 15% fee)
    - [x] Linked Account Management (Bank & PayPal, max 2)

**Legend:**
- [x] Complete
- [ ] Incomplete
- [~] Partially Complete / Basic Implementation

---

### Future Considerations / Deferred Items
- Full CAPTCHA implementation with a visual challenge.
- Live Twilio integration for OTP SMS.
- Implementation of actual email sending for admin notifications (e.g., via SendGrid/SMTP for KYC alerts, bank withdrawal processing).
- Advanced account recovery mechanisms.
- Production-grade IP/device tracking and rate limiting (e.g., using Redis/DB instead of in-memory stores).

---
