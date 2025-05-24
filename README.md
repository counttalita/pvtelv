# PATELA (PVTELV) Digital Wallet

PATELA is a modern digital wallet enabling secure deposits and withdrawals via PayPal and linked bank accounts. It features robust authentication, OTP security, risk analysis, and a seamless user experience.

---

## Project Structure

- `backend/` — Flask API backend (Python)
- `client/` — Frontend (Vite + React + TypeScript + shadcn-ui + Tailwind CSS)

---

## Key Features

### User Authentication
- Phone-based registration and login with OTP (rate-limited, lockouts, expiry).
- Primarily phone-based registration and login with OTP. Email is not actively used for user account verification or primary user communication.
- Device and network fingerprinting for risk analysis.
- Comprehensive audit logging and brute-force protection.

### Wallet Management
- Real-time wallet balance and transaction history.
- Top-up (deposit) via PayPal: User pays gross, 15% fee deducted, net amount credited to wallet.
- Withdrawals:
    - To Bank: Manual processing by admin.
    - To PayPal: Automated API-based payout.
- Linked bank account management (up to 2 per user).

### Security
- Strong validation for phone and payment details. Email is not collected from users during registration.
- Rate limiting, CAPTCHA threshold logging (no blocking CAPTCHA), and anomaly detection for suspicious activity.
- Session management with sliding expiry and multi-device support.

### Notifications
- SMS alerts for transactions and account changes. Email notifications are primarily for administrative purposes.
- Admin notifications for manual withdrawal processing.

---

## Core Flows

### Registration
1. **Phone Validation:** E.164 format, carrier checks, duplicate prevention.
2. **OTP Verification:** 6-digit code (mock Twilio), configured attempts, expiry, and lockout on abuse.
3. **Profile Creation:** Basic profile setup, welcome notification (in-app/SMS), onboarding instructions.

### Login
1. **Phone & Account Status:** Only verified, active accounts allowed.
2. **OTP Login:** Secure, rate-limited, session token generation
3. **Session Management:** 24h sliding expiry, multi-device, user-controlled session revocation

### Recovery
- Account recovery is primarily managed via phone number and OTP. Specific recovery scenarios beyond standard OTP login are subject to further development.

### Top-Up (PayPal)
1. User enters amount (ZAR 50.00 – ZAR 25,000.00).
2. PayPal payment link generated, internal transaction marked 'pending'.
3. On successful PayPal payment confirmation (via redirect or webhook):
    - User's wallet balance is credited with the top-up amount minus a 15% fee.
    - User is notified (in-app/SMS).

### Withdrawal
- **Bank:** User requests withdrawal. System validates balance, deducts gross amount (including a 15% fee). Admin is notified for manual processing of the net amount.
- **PayPal:** User requests withdrawal. System validates balance, deducts gross amount. A 15% fee is applied, and the net amount is sent to the user's PayPal account via API. User is notified.

---

## Technology Stack

- **Backend:** Python, Flask, SQLAlchemy, Twilio (mocked for OTP), PayPal SDK (`paypalrestsdk`).
- **Frontend:** React 18, Vite, TypeScript, shadcn-ui, Tailwind CSS, React Router, Zod.
- **Other:** SMS (via Twilio - mocked), device fingerprinting, robust logging.

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
