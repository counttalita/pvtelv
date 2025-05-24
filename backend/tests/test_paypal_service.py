import pytest
from unittest.mock import patch, MagicMock, Mock

# Assuming paypalrestsdk might not be installed in the test runner env,
# or we want to ensure it's always mocked.
# If it *is* installed, direct mocking of its classes/methods is fine.
# If not, we might need to add it to sys.modules for robust mocking.
# For now, let's assume it can be imported for mocking.
try:
    import paypalrestsdk
    # If the SDK is present, we can mock its exceptions
    PayPalResourceNotFound = paypalrestsdk.exceptions.ResourceNotFound
    PayPalWebhookEventVerificationError = paypalrestsdk.exceptions.WebhookEventVerificationError
except ImportError:
    # If paypalrestsdk is not installed, create mock exceptions to allow tests to run.
    # This is a common pattern for testing integrations with libraries that might be optional
    # or not present in all environments.
    class MockPayPalException(Exception): pass
    PayPalResourceNotFound = MockPayPalException
    PayPalWebhookEventVerificationError = MockPayPalException
    
    # Mock the paypalrestsdk module itself if it's not found
    # This is more advanced and might only be needed if basic @patch doesn't work.
    # For now, we'll assume @patch can handle it.


from services.paypal_service import (
    initialize_paypal,
    create_payment_order,
    execute_paypal_payment,
    verify_webhook_event,
    create_paypal_payout # Added this import
)
import logging
import uuid # For checking sender_item_id format if needed, though service generates it

# --- Tests for initialize_paypal ---

@patch('services.paypal_service.paypalrestsdk.configure')
def test_initialize_paypal_success(mock_paypal_configure):
    mock_config = {
        'PAYPAL_MODE': 'sandbox',
        'PAYPAL_CLIENT_ID': 'test_client_id',
        'PAYPAL_CLIENT_SECRET': 'test_client_secret'
    }
    result = initialize_paypal(mock_config)
    mock_paypal_configure.assert_called_once_with({
        "mode": 'sandbox',
        "client_id": 'test_client_id',
        "client_secret": 'test_client_secret'
    })
    assert result is True

@patch('services.paypal_service.paypalrestsdk.configure')
@patch('services.paypal_service.logging.error') # To check log messages
def test_initialize_paypal_missing_keys(mock_logging_error, mock_paypal_configure):
    mock_config = {'PAYPAL_MODE': 'sandbox'} # Missing client_id and client_secret
    result = initialize_paypal(mock_config)
    
    mock_logging_error.assert_called_once()
    # Check that the log message contains the missing keys
    assert "PAYPAL_CLIENT_ID" in mock_logging_error.call_args[0][0]
    assert "PAYPAL_CLIENT_SECRET" in mock_logging_error.call_args[0][0]
    
    mock_paypal_configure.assert_not_called()
    assert result is False

@patch('services.paypal_service.paypalrestsdk.configure', side_effect=Exception("SDK Config Error"))
@patch('services.paypal_service.logging.error')
def test_initialize_paypal_sdk_exception(mock_logging_error, mock_paypal_configure_exception):
    mock_config = {
        'PAYPAL_MODE': 'sandbox',
        'PAYPAL_CLIENT_ID': 'test_client_id',
        'PAYPAL_CLIENT_SECRET': 'test_client_secret'
    }
    result = initialize_paypal(mock_config)
    
    mock_paypal_configure_exception.assert_called_once()
    mock_logging_error.assert_called_once_with("Error initializing PayPal SDK: SDK Config Error")
    assert result is False

# --- Tests for create_payment_order ---

@patch('services.paypal_service.paypalrestsdk.Payment')
def test_create_payment_order_success(MockPaypalPayment):
    mock_payment_instance = MagicMock()
    mock_payment_instance.create.return_value = True
    mock_payment_instance.id = 'PAY-12345'
    # Mocking the links attribute which is expected to be an iterable of objects
    link_mock = MagicMock()
    link_mock.rel = 'approval_url'
    link_mock.href = 'http://localhost/approve'
    mock_payment_instance.links = [link_mock]
    
    MockPaypalPayment.return_value = mock_payment_instance

    result = create_payment_order(
        total_amount="10.00", 
        currency="USD", 
        return_url_approve="http://localhost/approve", 
        return_url_cancel="http://localhost/cancel"
    )

    MockPaypalPayment.assert_called_once() # Check if Payment constructor was called
    mock_payment_instance.create.assert_called_once() # Check if create method was called
    assert result == {
        "payment_id": 'PAY-12345',
        "approval_url": 'http://localhost/approve',
        "error": None
    }

@patch('services.paypal_service.paypalrestsdk.Payment')
def test_create_payment_order_paypal_error(MockPaypalPayment):
    mock_payment_instance = MagicMock()
    mock_payment_instance.create.return_value = False # Simulate PayPal error
    mock_payment_instance.error = {"name": "VALIDATION_ERROR", "message": "Invalid something."}
    MockPaypalPayment.return_value = mock_payment_instance

    result = create_payment_order("10.00", "USD", "approve_url", "cancel_url")

    assert "error" in result
    assert "PayPal payment creation failed" in result["error"]
    assert "VALIDATION_ERROR" in result["error"]

@patch('services.paypal_service.paypalrestsdk.Payment')
def test_create_payment_order_exception(MockPaypalPayment):
    mock_payment_instance = MagicMock()
    mock_payment_instance.create.side_effect = Exception("Connection timeout")
    MockPaypalPayment.return_value = mock_payment_instance

    result = create_payment_order("10.00", "USD", "approve_url", "cancel_url")

    assert "error" in result
    assert "An exception occurred" in result["error"]
    assert "Connection timeout" in result["error"]

@patch('services.paypal_service.paypalrestsdk.Payment')
def test_create_payment_order_no_approval_url(MockPaypalPayment):
    mock_payment_instance = MagicMock()
    mock_payment_instance.create.return_value = True
    mock_payment_instance.id = 'PAY-67890'
    mock_payment_instance.links = [] # No links, or no approval_url link
    MockPaypalPayment.return_value = mock_payment_instance

    result = create_payment_order("20.00", "EUR", "approve_url", "cancel_url")
    
    assert "error" in result
    assert result["error"] == "Could not find approval URL in PayPal response."


# --- Tests for execute_paypal_payment ---

@patch('services.paypal_service.paypalrestsdk.Payment')
def test_execute_paypal_payment_success(MockPaypalPaymentSDK):
    mock_payment_found = MagicMock()
    mock_payment_found.execute.return_value = True
    mock_payment_found.to_dict.return_value = {"state": "approved"} # Simulate to_dict
    
    MockPaypalPaymentSDK.find.return_value = mock_payment_found

    result = execute_paypal_payment(payment_id="PAY-123", payer_id="PAYER-ABC")

    MockPaypalPaymentSDK.find.assert_called_once_with("PAY-123")
    mock_payment_found.execute.assert_called_once_with({"payer_id": "PAYER-ABC"})
    assert result == {"success": True, "payment": {"state": "approved"}}

@patch('services.paypal_service.paypalrestsdk.Payment')
def test_execute_paypal_payment_failure(MockPaypalPaymentSDK):
    mock_payment_found = MagicMock()
    mock_payment_found.execute.return_value = False # Simulate execution failure
    mock_payment_found.error = {"name": "INSTRUMENT_DECLINED", "message": "Card declined."}
    MockPaypalPaymentSDK.find.return_value = mock_payment_found

    result = execute_paypal_payment(payment_id="PAY-456", payer_id="PAYER-DEF")

    assert result["success"] is False
    assert "INSTRUMENT_DECLINED" in result["error"]

@patch('services.paypal_service.paypalrestsdk.Payment.find', side_effect=PayPalResourceNotFound("Payment not found"))
def test_execute_paypal_payment_not_found(mock_payment_find_not_found):
    result = execute_paypal_payment(payment_id="PAY-NONEXISTENT", payer_id="PAYER-GHI")
    
    mock_payment_find_not_found.assert_called_once_with("PAY-NONEXISTENT")
    assert result["success"] is False
    assert result["error"] == "PayPal payment not found."

@patch('services.paypal_service.paypalrestsdk.Payment.find')
def test_execute_paypal_payment_find_exception(mock_payment_find):
    mock_payment_find.side_effect = Exception("Generic find error")
    result = execute_paypal_payment(payment_id="PAY-ERROR", payer_id="PAYER-JKL")
    assert result["success"] is False
    assert "Error finding PayPal payment: Generic find error" in result["error"]


@patch('services.paypal_service.paypalrestsdk.Payment')
def test_execute_paypal_payment_execute_exception(MockPaypalPaymentSDK):
    mock_payment_found = MagicMock()
    mock_payment_found.execute.side_effect = Exception("Execute blew up")
    MockPaypalPaymentSDK.find.return_value = mock_payment_found

    result = execute_paypal_payment(payment_id="PAY-EXEC-FAIL", payer_id="PAYER-MNO")
    assert result["success"] is False
    assert "An exception occurred while executing PayPal payment: Execute blew up" in result["error"]


# --- Tests for verify_webhook_event ---

@patch('services.paypal_service.paypalrestsdk.WebhookEvent.verify')
def test_verify_webhook_event_success(mock_webhook_verify):
    mock_event_data = MagicMock() # Simulate a WebhookEvent object
    mock_event_data.id = "EVT-123"
    mock_webhook_verify.return_value = mock_event_data
    
    headers = {'Paypal-Transmission-Id': 'tx_id'} # Example header
    result = verify_webhook_event("raw_body_data", headers, "WEBHOOK-ID-123")

    mock_webhook_verify.assert_called_once()
    # More detailed assertion on args passed to verify can be added if needed
    assert result == mock_event_data

@patch('services.paypal_service.paypalrestsdk.WebhookEvent.verify', side_effect=PayPalWebhookEventVerificationError("Verification failed"))
def test_verify_webhook_event_verification_error(mock_webhook_verify_error):
    result = verify_webhook_event("body", {}, "WEBHOOK-ID-XYZ")
    
    assert result is None

@patch('services.paypal_service.logging.error')
def test_verify_webhook_event_missing_webhook_id(mock_logging_error):
    result = verify_webhook_event("body", {}, None) # expected_webhook_id is None
    
    mock_logging_error.assert_called_once_with("PayPal Webhook: PAYPAL_WEBHOOK_ID is not configured in the application.")
    assert result is None

@patch('services.paypal_service.paypalrestsdk.WebhookEvent.verify', side_effect=Exception("Unexpected SDK error"))
@patch('services.paypal_service.logging.exception')
def test_verify_webhook_event_unexpected_exception(mock_logging_exception, mock_webhook_verify_unexpected_error):
    result = verify_webhook_event("body", {}, "WEBHOOK-ID-ABC")

    mock_logging_exception.assert_called_once()
    assert "PayPal Webhook: An unexpected error occurred during webhook verification: Unexpected SDK error" in mock_logging_exception.call_args[0][0]
    assert result is None

# TODO: Add tests for verify_webhook_event with more specific header checks if necessary
# to ensure all required parts (transmission_id, timestamp, cert_url, actual_signature)
# are correctly passed to paypalrestsdk.WebhookEvent.verify.
# This might involve checking the `call_args` of `mock_webhook_verify`.

# --- Tests for create_paypal_payout ---

@patch('services.paypal_service.paypalrestsdk.Payout')
def test_create_paypal_payout_success(MockPaypalPayoutSDK):
    mock_payout_instance = MagicMock()
    mock_payout_instance.create.return_value = True # Simulate successful Payout.create()
    
    # Mock the structure returned by payout.to_dict() and attributes
    mock_payout_instance.batch_header = MagicMock()
    mock_payout_instance.batch_header.payout_batch_id = 'BATCH-ID-123'
    
    # Simulate the items list with one item and its transaction_status
    mock_item = MagicMock()
    mock_item.transaction_status = 'SUCCESS' # Direct attribute access
    # If to_dict() is called on items, then mock that structure:
    mock_item_dict = {"transaction_status": "SUCCESS"} 
    # To handle payout.to_dict(), which would call to_dict on nested objects:
    mock_payout_instance.to_dict.return_value = {
        "batch_header": {"payout_batch_id": "BATCH-ID-123"},
        "items": [mock_item_dict] # Correctly mock the list of dicts
    }
    # If the code accesses payout.items[0].transaction_status directly:
    # We need to ensure payout.items is a list of objects that have transaction_status
    # The Payout SDK usually returns objects that can be converted to dicts
    # Let's assume the service uses .to_dict() for the details part
    # and direct attribute access for payout_batch_id.
    # The service implementation does: `payout.batch_header.payout_batch_id` and `payout.to_dict()`
    
    MockPaypalPayoutSDK.return_value = mock_payout_instance

    result = create_paypal_payout(
        recipient_email="receiver@example.com",
        amount_value="50.00",
        currency="USD",
        internal_payout_id="internal_tx_1",
        sync_mode=True
    )

    MockPaypalPayoutSDK.assert_called_once() # Check Payout constructor
    # Check args of Payout constructor if needed, especially sender_batch_id truncation
    constructor_args, _ = MockPaypalPayoutSDK.call_args
    payout_data_arg = constructor_args[0]
    assert payout_data_arg['sender_batch_header']['sender_batch_id'] == 'internal_tx_1'
    assert payout_data_arg['items'][0]['amount']['value'] == '50.00'
    assert payout_data_arg['items'][0]['receiver'] == 'receiver@example.com'
    
    mock_payout_instance.create.assert_called_once()
    
    assert result["success"] is True
    assert result["payout_batch_id"] == 'BATCH-ID-123'
    assert result["details"]["items"][0]["transaction_status"] == "SUCCESS"


@patch('services.paypal_service.paypalrestsdk.Payout')
def test_create_paypal_payout_sender_batch_id_truncation(MockPaypalPayoutSDK, caplog):
    mock_payout_instance = MagicMock()
    mock_payout_instance.create.return_value = True
    mock_payout_instance.batch_header = MagicMock()
    mock_payout_instance.batch_header.payout_batch_id = 'BATCH-ID-TRUNC'
    mock_payout_instance.to_dict.return_value = {
        "batch_header": {"payout_batch_id": "BATCH-ID-TRUNC"},
        "items": [{"transaction_status": "SUCCESS"}]
    }
    MockPaypalPayoutSDK.return_value = mock_payout_instance

    long_internal_id = "this_is_a_very_long_internal_payout_id_that_exceeds_thirty_characters_limit"
    expected_truncated_id = long_internal_id[:30]

    with caplog.at_level(logging.WARNING):
        result = create_paypal_payout(
            recipient_email="receiver@example.com",
            amount_value="20.00",
            currency="EUR",
            internal_payout_id=long_internal_id
        )
    
    assert result["success"] is True
    constructor_args, _ = MockPaypalPayoutSDK.call_args
    payout_data_arg = constructor_args[0]
    assert payout_data_arg['sender_batch_header']['sender_batch_id'] == expected_truncated_id
    assert f"PayPal Payout: sender_batch_id '{long_internal_id}' was truncated to 30 chars." in caplog.text


@patch('services.paypal_service.paypalrestsdk.Payout')
def test_create_paypal_payout_paypal_error(MockPaypalPayoutSDK):
    mock_payout_instance = MagicMock()
    mock_payout_instance.create.return_value = False # Simulate Payout.create() failure
    mock_payout_instance.error = {"name": "PAYOUT_DENIED", "message": "Payouts not enabled."}
    MockPaypalPayoutSDK.return_value = mock_payout_instance

    result = create_paypal_payout("test@example.com", "30.00", "CAD", "internal_tx_2")

    assert result["success"] is False
    assert result["error"] == {"name": "PAYOUT_DENIED", "message": "Payouts not enabled."}

@patch('services.paypal_service.paypalrestsdk.Payout')
def test_create_paypal_payout_sdk_exception(MockPaypalPayoutSDK):
    # Simulate an exception from the SDK that is a PayPalError
    # The actual PayPalError has response and message attributes
    mock_sdk_error = paypalrestsdk.exceptions.PayPalError(
        message="SDK Internal Error", 
        response=Mock(status_code=500, text='{"name":"INTERNAL_SERVICE_ERROR","message":"An internal service error occurred."}')
    )
    mock_payout_instance = MagicMock()
    mock_payout_instance.create.side_effect = mock_sdk_error
    MockPaypalPayoutSDK.return_value = mock_payout_instance

    result = create_paypal_payout("test@example.com", "25.00", "GBP", "internal_tx_3")

    assert result["success"] is False
    assert "SDK Internal Error" in str(result["error"]) # Check that the original message is part of the error
    assert result["details"] is not None # Check that response details are included if available


@patch('services.paypal_service.paypalrestsdk.Payout')
def test_create_paypal_payout_generic_exception(MockPaypalPayoutSDK):
    mock_payout_instance = MagicMock()
    mock_payout_instance.create.side_effect = Exception("A generic network error")
    MockPaypalPayoutSDK.return_value = mock_payout_instance

    result = create_paypal_payout("test@example.com", "10.00", "AUD", "internal_tx_4")

    assert result["success"] is False
    assert "A generic network error" in result["error"]
```
