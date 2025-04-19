from app.kyc import KYCSubmission
from app.db import db
from datetime import datetime

# Additional KYC business logic can be added here.

def submit_kyc(user_id, documents):
    valid, error = validate_documents(documents)
    if not valid:
        raise ValueError(f'Invalid KYC documents: {error}')
    status, provider_result = integrate_with_provider(documents, user_id)
    import json
    if isinstance(provider_result, dict):
        provider_result_str = json.dumps(provider_result)
    else:
        provider_result_str = str(provider_result)
    sub = KYCSubmission(user_id=user_id, documents=documents, status=status, result=provider_result_str)
    db.session.add(sub)
    db.session.commit()
    trigger_kyc_status_notification(user_id, status)
    return sub


def get_kyc_status(user_id):
    sub = KYCSubmission.query.filter_by(user_id=user_id).order_by(KYCSubmission.submitted_at.desc()).first()
    if not sub:
        return 'not_submitted', None
    return sub.status, sub


def review_kyc(submission_id, status, notes=None):
    sub = KYCSubmission.query.get(submission_id)
    if sub:
        sub.status = status
        sub.reviewed_at = datetime.utcnow()
        sub.notes = notes
        db.session.commit()
        trigger_kyc_status_notification(sub.user_id, status)
        return True
    return False

def validate_documents(documents):
    """
    Validate document types/structure. Stub: returns True if docs look like JSON.
    Replace with real validation logic as needed.
    """
    try:
        import json
        docs = json.loads(documents)
        # Example: require 'id_card' and 'selfie'
        required = {'id_card', 'selfie'}
        if not required.issubset(docs.keys()):
            return False, 'Missing required documents.'
        return True, ''
    except Exception as e:
        return False, f'Invalid document format: {e}'


def integrate_with_provider(documents, user_id):
    """
    Integrate with external KYC provider. For MVP, this sends KYC documents to pbang@tosh.co.za for manual review.
    Returns status ('pending_manual') and provider result (dict).
    """
    import smtplib
    from email.message import EmailMessage
    import os
    # Compose email
    msg = EmailMessage()
    msg['Subject'] = f'KYC Submission for User {user_id}'
    msg['From'] = os.environ.get('KYC_FROM_EMAIL', 'noreply@mvp.local')
    msg['To'] = 'pbang@tosh.co.za'
    msg.set_content(f'User ID: {user_id}\nKYC Documents:\n{documents}')
    try:
        smtp_server = os.environ.get('KYC_SMTP_SERVER', 'localhost')
        smtp_port = int(os.environ.get('KYC_SMTP_PORT', 25))
        smtp_user = os.environ.get('KYC_SMTP_USER')
        smtp_pass = os.environ.get('KYC_SMTP_PASS')
        if smtp_user and smtp_pass:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.send_message(msg)
    except Exception as e:
        # Log but do not fail KYC submission for MVP
        print(f"[MVP KYC] Failed to send email for manual review: {e}")
    # Always return pending_manual for MVP
    return 'pending_manual', {'provider': 'manual_email', 'details': 'sent to pbang@tosh.co.za for manual review'}


def trigger_kyc_status_notification(user_id, status):
    """
    Trigger notification (email, SMS, in-app) on KYC status change.
    Stub: just log or print.
    """
    print(f'Notify user {user_id}: KYC status changed to {status}')
