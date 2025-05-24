import paypalrestsdk
import logging # Optional, for logging init status
import uuid # For unique sender_item_id

# Configure logging (optional, but good practice)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_paypal(config):
    """Initializes the PayPal SDK with credentials from the app config."""
    # Check if essential PayPal configuration keys are present
    required_keys = ['PAYPAL_MODE', 'PAYPAL_CLIENT_ID', 'PAYPAL_CLIENT_SECRET']
    missing_keys = [key for key in required_keys if not config.get(key)]
    
    if missing_keys:
        logging.error(f"PayPal SDK initialization failed. Missing required config keys: {', '.join(missing_keys)}")
        return False
        
    try:
        paypalrestsdk.configure({
            "mode": config.get('PAYPAL_MODE'),
            "client_id": config.get('PAYPAL_CLIENT_ID'),
            "client_secret": config.get('PAYPAL_CLIENT_SECRET')
        })
        logging.info("PayPal SDK initialized successfully.") # Optional
        return True
    except Exception as e:
        logging.error(f"Error initializing PayPal SDK: {e}") # Optional
        return False

def create_payment_order(total_amount: str, currency: str, return_url_approve: str, return_url_cancel: str):
    """
    Creates a PayPal payment order and returns the approval URL.
    total_amount should be a string (e.g., "10.00").
    """
    payment_details = {
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": return_url_approve,
            "cancel_url": return_url_cancel
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "PVTElA Wallet Top-Up",
                    "sku": "WTU001", # Stock Keeping Unit - can be generic
                    "price": str(total_amount), # Must be string
                    "currency": currency.upper(),
                    "quantity": "1"
                }]
            },
            "amount": {
                "total": str(total_amount), # Must be string
                "currency": currency.upper()
            },
            "description": "PVTElA Digital Wallet Top-Up"
        }]
    }

    payment = paypalrestsdk.Payment(payment_details)

    try:
        if payment.create():
            # Find the approval URL
            approval_url = None
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = str(link.href) # Ensure it's a string
                    break
            
            if approval_url:
                return {
                    "payment_id": payment.id,
                    "approval_url": approval_url,
                    "error": None
                }
            else:
                logging.error("PayPal: Could not find approval URL in payment response. Payment ID: %s", payment.id)
                return {"error": "Could not find approval URL in PayPal response."}
        else:
            # payment.error contains details of the error
            error_details = payment.error if hasattr(payment, 'error') and payment.error else "Unknown error during payment creation."
            logging.error("PayPal payment creation failed: %s. Payment ID: %s", error_details, payment.id if hasattr(payment, 'id') else 'N/A')
            return {"error": f"PayPal payment creation failed: {error_details}"}
    except Exception as e:
        logging.exception("PayPal: An exception occurred while creating PayPal payment.") # Logs traceback
        return {"error": f"An exception occurred while creating PayPal payment: {str(e)}"}

def execute_paypal_payment(payment_id: str, payer_id: str):
    """
    Executes a PayPal payment that has been approved by the user.
    """
    try:
        payment = paypalrestsdk.Payment.find(payment_id)
    except paypalrestsdk.exceptions.ResourceNotFound:
        logging.error(f"PayPal: Payment with ID {payment_id} not found.")
        return {"success": False, "error": "PayPal payment not found."}
    except Exception as e:
        logging.exception(f"PayPal: Error finding payment {payment_id}.")
        return {"success": False, "error": f"Error finding PayPal payment: {str(e)}"}

    if payment:
        try:
            if payment.execute({"payer_id": payer_id}):
                # Consider what parts of payment object are useful to return
                # For now, returning a simplified success and the payment details
                return {"success": True, "payment": payment.to_dict()} 
            else:
                error_details = payment.error if hasattr(payment, 'error') and payment.error else "Unknown error during payment execution."
                logging.error(f"PayPal payment execution failed: {error_details}. Payment ID: {payment_id}")
                return {"success": False, "error": error_details}
        except Exception as e:
            logging.exception(f"PayPal: An exception occurred while executing payment {payment_id}.")
            return {"success": False, "error": f"An exception occurred while executing PayPal payment: {str(e)}"}
    else:
        # This case should ideally be caught by ResourceNotFound, but as a fallback
        logging.error(f"PayPal: Payment {payment_id} could not be retrieved for execution (should have been caught by find).")
        return {"success": False, "error": "PayPal payment could not be retrieved for execution."}


def verify_webhook_event(request_data_decode: str, request_headers: dict, expected_webhook_id: str):
    """
    Verifies a PayPal webhook event.
    Args:
        request_data_decode: The raw decoded request body string.
        request_headers: Dictionary of request headers.
        expected_webhook_id: The webhook ID configured in your PayPal app.
    Returns:
        The verified paypalrestsdk.WebhookEvent object if verification is successful,
        None otherwise.
    """
    if not expected_webhook_id:
        logging.error("PayPal Webhook: PAYPAL_WEBHOOK_ID is not configured in the application.")
        return None

    try:
        # The SDK's verify method may look for specific header keys.
        # Ensure that the request_headers dict passed contains what the SDK expects,
        # e.g., 'PAYPAL-TRANSMISSION-ID', 'PAYPAL-SIGNATURE', 'PAYPAL-CERT-URL', etc.
        # The SDK handles fetching the cert and verifying the signature.
        event = paypalrestsdk.WebhookEvent.verify(
            transmission_id=request_headers.get('Paypal-Transmission-Id'), # Case-insensitive dict lookup might be better
            timestamp=request_headers.get('Paypal-Transmission-Time'),
            webhook_id=expected_webhook_id, # Your Webhook ID from PayPal dev portal
            event_body=request_data_decode, # Raw request body
            cert_url=request_headers.get('Paypal-Cert-Url'),
            actual_signature=request_headers.get('Paypal-Transmission-Sig'),
            # auth_algo=request_headers.get('Paypal-Auth-Algo') # Optional, SDK might default
        )
        logging.info(f"PayPal Webhook: Event verification successful. Event ID: {event.id if event else 'N/A'}")
        return event
    except paypalrestsdk.exceptions.WebhookEventVerificationError as e:
        logging.error(f"PayPal Webhook: Verification failed: {e}")
        return None
    except Exception as e:
        # Log the full traceback for unexpected errors
        logging.exception(f"PayPal Webhook: An unexpected error occurred during webhook verification: {e}")
        return None

# (No other placeholders were mentioned, so this can be removed if not needed)

def create_paypal_payout(recipient_email: str, amount_value: str, currency: str, 
                         internal_payout_id: str, sync_mode: bool = True):
    """
    Creates and processes a PayPal Payout.
    """
    sender_batch_id = str(internal_payout_id) 
    if len(sender_batch_id) > 30:
        # Simple truncation for this example. Hashing or a more robust unique ID generation
        # might be needed if internal_payout_id is frequently longer and needs to be reversible
        # or more uniquely represented within 30 chars.
        logging.warning(f"PayPal Payout: sender_batch_id '{sender_batch_id}' was truncated to 30 chars.")
        sender_batch_id = sender_batch_id[:30]

    # A unique ID for this specific item within the batch.
    # PayPal requires sender_item_id to be unique for each item in a batch.
    # If your internal_payout_id already represents a single item, it could be used,
    # but if internal_payout_id is for the batch, then items need unique IDs.
    payout_item_id = str(uuid.uuid4()) 

    payout_data = {
        "sender_batch_header": {
            "sender_batch_id": sender_batch_id,
            "email_subject": "You have received a payout from PVTElA Digital Wallet",
            "email_message": "You have received a payment from PVTElA Digital Wallet. Thank you for using our service!"
        },
        "items": [
            {
                "recipient_type": "EMAIL",
                "amount": {
                    "value": str(amount_value), # Ensure amount is string
                    "currency": currency.upper()
                },
                "note": "Thank you for your withdrawal from PVTElA.",
                "sender_item_id": payout_item_id, 
                "receiver": recipient_email
            }
        ]
    }

    try:
        # sync_mode=True: The call waits for processing to complete.
        # sync_mode=False (default): The call is asynchronous.
        # For Payouts, even in sync_mode=True, the batch status might go through PENDING/PROCESSING first.
        # The item status (transaction_status) is key for individual payout success.
        payout = paypalrestsdk.Payout(payout_data, sync_mode=sync_mode)

        if payout.create():
            # If sync_mode=True, the response directly contains the status of the batch and items.
            # payout.batch_header.batch_status -> BATCH_STATUS (e.g., PENDING, PROCESSING, SUCCESS, DENIED)
            # payout.items[0].transaction_status -> ITEM_STATUS (e.g., SUCCESS, FAILED, PENDING, UNCLAIMED)
            
            # For simplicity, we'll return the whole payout object details.
            # The caller (route handler) will need to inspect these details.
            return {
                "success": True, 
                "payout_batch_id": payout.batch_header.payout_batch_id if payout.batch_header else None, 
                "details": payout.to_dict() # Full response for detailed checking
            }
        else:
            # payout.error contains details of the error
            error_details = payout.error if hasattr(payout, 'error') and payout.error else "Unknown error during payout creation."
            logging.error(f"PayPal Payout creation failed: {error_details}. Batch ID attempt: {sender_batch_id}")
            return {"success": False, "error": error_details}
    except paypalrestsdk.exceptions.PayPalError as e:
        # More specific PayPal SDK error
        logging.exception(f"PayPal SDK Error during PayPal Payout for batch {sender_batch_id}: {e}")
        # e.message might be a dict or string, ensure it's serializable
        error_message = e.message if isinstance(e.message, str) else str(e.message)
        return {"success": False, "error": error_message, "details": e.response if hasattr(e, 'response') else None}
    except Exception as e:
        logging.exception(f"Generic exception during PayPal Payout for batch {sender_batch_id}: {e}")
        return {"success": False, "error": str(e)}
