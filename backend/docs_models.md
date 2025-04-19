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

---

_Last updated: 2025-04-19_
