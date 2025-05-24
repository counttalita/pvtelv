# PVTElA Digital Wallet MVP

## Overview
PVTElA is a secure, mobile-first digital wallet MVP designed to demonstrate robust registration, login, onboarding, and KYC (Know Your Customer) flows. This project is built with Flask, SQLAlchemy, and a modular service architecture. It features strong security, manual KYC integration, and comprehensive test coverage.

---

## Features

### Registration & Login
- E.164 phone validation, disposable/VoIP check, carrier/region restrictions
- Duplicate account prevention
- OTP generation, hashing, expiry, and rate limiting (OTP generation uses a mock Twilio service.)
- Device and IP fingerprinting
- Suspicious activity detection and CAPTCHA threshold logging (full CAPTCHA implementation deferred).
- Audit logging for all critical events

### KYC (Know Your Customer)
- Manual KYC document submission (documents are emailed for review)
- Status tracking: pending_manual, approved, rejected
- All KYC flows tested and verifiable

### Onboarding & Profile
- Profile creation after KYC approval
- Welcome notification (in-app and SMS; email is not used for user notifications).
- Intro tour and security setup steps
- User preferences and onboarding completion tracking

### Session Management
- JWT-based session tokens with sliding expiry
- Multi-device and multi-location support
- Session revocation and validation

### Security
- Rate limiting for OTP and registration attempts
- In-memory suspicious IP/device tracking (MVP)
- Audit trail for all sensitive actions

### Wallet Management
- User wallet with real-time balance.
- Comprehensive transaction history (deposits, withdrawals, fees).
- Top-up via PayPal (15% fee applied, user pays gross, net amount credited).
- Withdrawals to linked bank accounts (manual admin processing, 15% fee applied to amount withdrawn) and linked PayPal accounts (automated Payouts API, 15% fee applied to amount withdrawn).
- Management of linked bank and PayPal accounts (max 2 per user).

---

## Project Structure

- `app/` - Main Flask app and blueprints
- `services/` - Business logic and integrations (OTP, KYC, security, etc.)
- `tests/` - Pytest-based test suite for all major flows
- `requirements.txt` - Python dependencies

---

## Setup & Usage

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd pvtelv
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure environment:**
   - Copy `.env.example` to `.env` and set required variables (see below).
4. **Run the app:**
   ```sh
   python run.py
   ```
5. **Run tests:**
   ```sh
   pytest tests/
   ```

---

## Environment Variables

- `DATABASE_URL` - SQLAlchemy DB URI (default: SQLite)
- `JWT_SECRET` - Secret for JWT encoding
- `KYC_FROM_EMAIL`, `KYC_SMTP_SERVER`, `KYC_SMTP_PORT`, `KYC_SMTP_USER`, `KYC_SMTP_PASS` - For KYC email integration
- `PAYPAL_MODE` - PayPal API mode ('sandbox' or 'live').
- `PAYPAL_CLIENT_ID` - PayPal Client ID.
- `PAYPAL_CLIENT_SECRET` - PayPal Client Secret.
- `PAYPAL_WEBHOOK_ID` - PayPal Webhook ID for verifying incoming event notifications.
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` - Twilio credentials for SMS (currently, OTP service uses a MOCKED Twilio implementation).

---

## Testing
- All flows are covered by tests in `tests/`.
- Run `pytest tests/` after each change to ensure reliability.

---

## Current Status
- Core MVP features including registration, login, KYC, onboarding, and comprehensive wallet management (PayPal top-up, bank/PayPal withdrawals, fees, transaction history, linked accounts) are implemented and tested. The OTP service uses a MOCKED Twilio implementation. Full CAPTCHA implementation is deferred. Admin email notifications (e.g., for KYC, bank withdrawals) require configuration of an external email sending service.

---

## License
MIT License
