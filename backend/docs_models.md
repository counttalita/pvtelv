# PVTElA Data Models

This document describes the main SQLAlchemy models used in the PVTElA MVP.

---

## User
- `id`: Integer, primary key
- `phone`: String, unique, E.164 format
- `phone_verified`: Boolean
- `otp_hash`, `otp_expiry`, `otp_attempts`, `otp_last_requested`, `otp_lockout_until`: OTP management
- `device_fingerprint`, `registration_ip`, `registration_location`: Device/network info
- `failed_otp_attempts`, `last_otp_failure`: OTP failure tracking
- `role`: User/admin
- `email`: String, unique, nullable (Note: For optional administrative use; not part of primary user registration/verification flow).
- `email_verified`: Boolean, default False (Companion to the email field).

## KYCSubmission
- `id`: Integer, primary key
- `user_id`: Integer, foreign key
- `status`: String ('pending_manual', 'approved', 'rejected')
- `submitted_at`, `reviewed_at`: Datetime
- `result`: String/JSON (provider response)
- `documents`: Text (JSON or file paths)
- `notes`: Text (manual review notes)

## ActiveSession
- `id`: Integer, primary key
- `user_id`: Integer, foreign key
- `device_fingerprint`: String
- `jti`: String (JWT ID)
- `issued_at`, `expires_at`: Datetime
- `revoked`: Boolean
- `last_seen`: Datetime

## UserProfile
- `id`: Integer, primary key
- `user_id`: Integer, foreign key (unique)
- `created_at`: Datetime
- `display_name`: String
- `welcome_sent`, `onboarding_completed`: Boolean
- `preferences`: Text (JSON)
- `intro_tour_complete`, `security_setup_complete`: Boolean

## AuditLog
- `id`: Integer, primary key
- `event_type`: String
- `phone`, `ip`, `device_fingerprint`: String
- `status`: String
- `timestamp`: Datetime
- `details`: String

## Wallet
- `id`: Integer, primary key
- `user_id`: Integer, foreign key to `user.id`, unique (each user has one wallet)
- `balance`: Numeric(10, 2), nullable=False, default=0.00
- `created_at`: Datetime, default=datetime.utcnow
- `updated_at`: Datetime, default=datetime.utcnow, onupdate=datetime.utcnow

## Transaction
- `id`: Integer, primary key
- `wallet_id`: Integer, foreign key to `wallet.id`, nullable=False
- `type`: String, nullable=False (e.g., 'deposit', 'withdrawal', 'fee')
- `amount`: Numeric(10, 2), nullable=False
- `currency`: String(3), nullable=False, default='ZAR'
- `status`: String, nullable=False (e.g., 'pending', 'completed', 'failed', 'pending_manual', 'cancelled', 'processing_payout', 'pending_paypal_confirmation')
- `timestamp`: Datetime, default=datetime.utcnow
- `description`: String(255), nullable=True
- `external_transaction_id`: String(100), nullable=True, unique=True, index=True (For PayPal transaction IDs, payout batch IDs, etc.)

## LinkedAccount
- `id`: Integer, primary key
- `user_id`: Integer, foreign key to `user.id`, nullable=False
- `account_type`: String, nullable=False (e.g., 'bank', 'paypal')
- `account_details`: JSON, nullable=False (Stores bank details or PayPal email/ID)
- `friendly_name`: String(100), nullable=True (e.g., "My Savings", "Primary PayPal")
- `is_verified`: Boolean, default=False, nullable=False
- `created_at`: Datetime, default=datetime.utcnow

---

_Last updated: 2025-04-20_
