# PVTElA Digital Wallet MVP

## Overview
PVTElA is a secure, mobile-first digital wallet MVP designed to demonstrate robust registration, login, onboarding, and KYC (Know Your Customer) flows. This project is built with Flask, SQLAlchemy, and a modular service architecture. It features strong security, manual KYC integration, and comprehensive test coverage.

---

## Features

### Registration & Login
- E.164 phone validation, disposable/VoIP check, carrier/region restrictions
- Duplicate account prevention
- OTP generation, hashing, expiry, and rate limiting
- Device and IP fingerprinting
- Suspicious activity detection and CAPTCHA triggers
- Audit logging for all critical events

### KYC (Know Your Customer)
- Manual KYC document submission (documents are emailed for review)
- Status tracking: pending_manual, approved, rejected
- All KYC flows tested and verifiable

### Onboarding & Profile
- Profile creation after KYC approval
- Welcome notification (in-app, with hooks for email/SMS)
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

---

## Testing
- All flows are covered by tests in `tests/`.
- Run `pytest tests/` after each change to ensure reliability.

---

## MVP Status
- Registration, login, onboarding, and KYC flows are complete and robust.
- All tests are passing.
- Next step: Wallet/account setup after onboarding.

---

## License
MIT License
