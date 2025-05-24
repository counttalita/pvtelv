# PVTElA Architecture Overview

## High-Level Architecture

PVTElA is built on a modular service-oriented architecture using Flask as the web framework and SQLAlchemy as the ORM. The system is designed for extensibility, security, and testability.

### Key Components

- **Flask App:** Entry point, configures blueprints and extensions.
- **Blueprints:** Route grouping for registration, login, KYC, profile, etc.
    - `/api/wallet` (routes defined in `routes_wallet.py`): Exposes endpoints for wallet functionalities including PayPal top-ups, bank/PayPal withdrawals, and linked account management.
- **Services:** Contain business logic for OTP, KYC, security, notifications, etc.
    - `paypal_service.py`: Handles interactions with the PayPal API for processing payments (deposits via PayPal Payments) and payouts (withdrawals to PayPal).
    - `wallet_service.py`: Manages user wallet creation and the logging of financial transactions.
    - `linked_account_service.py`: Manages CRUD operations for user's linked bank and PayPal accounts used for withdrawals.
- **Models:** SQLAlchemy models for users, sessions, KYC submissions, profiles, and audit logs.
- **Tests:** Pytest-based suite covering all flows.

### Flow Diagram

```
[Client]
   |
   v
[Flask App / Blueprints]
   |
   v
[Services Layer] <-> [Models (DB)]
   |
   v
[External Integrations (Email, SMS, KYC, etc.)]
```

### User Interaction Model
User interaction and authentication are primarily phone/OTP based. Email is de-emphasized for user-facing account verification and communication, mainly reserved for administrative notifications.

---

## Security Considerations
- OTP and session rate limiting
- Device/IP fingerprinting
- Audit logging for sensitive actions
- Manual KYC review (MVP)
- Transaction fee model (e.g., a 15% fee on certain transactions like deposits and withdrawals) is implemented.
- CAPTCHA threshold logging based on OTP failures is in place (full visual CAPTCHA implementation is deferred).

---

## Extending the Architecture
- Add new blueprints for features (e.g., wallet, payments)
- Add new models/services as needed
- Swap in production-ready integrations (e.g., real KYC APIs, Redis for rate limiting)

---

_Last updated: 2025-04-20_
