import os
import requests

def send_email(to_email, subject, body):
    # Stub: Integrate with SendGrid, Mailgun, or SMTP
    print(f"[EMAIL] To: {to_email}\nSubject: {subject}\n{body}")
    # Example: requests.post('https://api.sendgrid.com/v3/mail/send', ...)


def send_sms(to_phone, body):
    import os
    from requests.auth import HTTPBasicAuth
    TWILIO_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_FROM = os.environ.get('TWILIO_FROM_NUMBER')
    if TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM:
        url = f'https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json'
        data = {
            'From': TWILIO_FROM,
            'To': to_phone,
            'Body': body
        }
        try:
            resp = requests.post(url, data=data, auth=HTTPBasicAuth(TWILIO_SID, TWILIO_TOKEN))
            resp.raise_for_status()
            print(f"[TWILIO] SMS sent to {to_phone}")
        except Exception as e:
            print(f"[TWILIO] SMS failed to {to_phone}: {e}")
    else:
        print(f"[SMS] To: {to_phone}\n{body}")


def send_inapp(user_id, body):
    # Stub: In-app notification system
    print(f"[IN-APP] User: {user_id}\n{body}")
