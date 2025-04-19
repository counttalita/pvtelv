# PATELA (PVTELV) Digital Wallet

PATELA is a modern digital wallet enabling secure deposits and withdrawals via PayPal and linked bank accounts. It features robust authentication, OTP security, risk analysis, and a seamless user experience.

---

## Project Structure

- `backend/` — Flask API backend (Python)
- `client/` — Frontend (Vite + React + TypeScript + shadcn-ui + Tailwind CSS)

---

## Key Features

### User Authentication
- Phone-based registration and login with OTP (rate-limited, lockouts, expiry)
- Email verification and multi-factor onboarding
- Device and network fingerprinting for risk analysis
- Comprehensive audit logging and brute-force protection

### Wallet Management
- Real-time wallet balance and transaction history
- Top-up (deposit) via PayPal with dynamic fee calculation
- Withdrawals to bank or PayPal with manual/automated processing
- Linked bank account management (up to 2 per user)

### Security
- Strong validation for phone, email, and payment details
- Rate limiting, CAPTCHA, and anomaly detection for suspicious activity
- Session management with sliding expiry and multi-device support

### Notifications
- Email and SMS alerts for transactions and account changes
- Admin notifications for manual withdrawal processing

---

## Core Flows

### Registration
1. **Phone Validation:** E.164 format, carrier checks, duplicate prevention
2. **OTP Verification:** 6-digit code via Twilio, 3 attempts, 5 min expiry, lockout on abuse
3. **Profile Creation:** Risk scoring, welcome notification, onboarding instructions
4. **Email Verification:** Token-based, 24h expiry, increases verification level

### Login
1. **Phone & Account Status:** Only verified, active accounts allowed
2. **OTP Login:** Secure, rate-limited, session token generation
3. **Session Management:** 24h sliding expiry, multi-device, user-controlled session revocation

### Recovery
- **Phone:** Email verification required, cooling-off period, notify previous number
- **Email:** OTP + reset token, notify linked phone, lock sensitive actions

### Top-Up (PayPal)
1. User enters amount (R50–R25,000), system calculates fees
2. PayPal payment link generated, transaction marked pending
3. On success: update balance (minus 15% fee), notify user

### Withdrawal
- **Bank:** Validate balance, 15% fee, admin notified for manual processing
- **PayPal:** Validate, deduct fees, initiate payout, notify user

---

## Technology Stack

- **Backend:** Python, Flask, Appwrite, Twilio, PayPal SDK
- **Frontend:** React 18, Vite, TypeScript, shadcn-ui, Tailwind CSS, React Router, Zod
- **Other:** Email/SMS (Twilio), device fingerprinting, robust logging

---

## Setup & Development

### Backend

1. `cd backend`
2. (Recommended) `python3 -m venv venv && source venv/bin/activate`
3. `pip install -r requirements.txt`
4. Create a `.env` file with your secrets (never commit this!)
5. `PYTHONPATH=. python run.py`

### Frontend

1. `cd client`
2. `npm install`
3. `npm run dev`

---

## Security & Best Practices

- **Never commit `.env` or secrets.** Always add to `.gitignore`.
- **Rotate all secrets** if they have ever been pushed to a public repo.
- **Production:** Use HTTPS, secure API keys, and enable server-side monitoring.

---

## Contributing

- Use feature branches and pull requests.
- Write clear commit messages and document major changes.
- Keep secrets out of code and version control.

---

## License

MIT

---

*For more detailed flow and business logic, see the `/backend/PVTElA_PROGRESS.md` or internal documentation.*
