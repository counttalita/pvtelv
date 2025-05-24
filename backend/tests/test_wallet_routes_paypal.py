import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from flask import url_for, current_app

from app import create_app
from app.db import db
from app.models import User
from app.wallet import Wallet, Transaction # Assuming Transaction is here

# --- Fixtures ---

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    # Required for url_for with _external=True if routes are not in app context during test setup
    app.config['SERVER_NAME'] = 'localhost.test' 
    app.config['SECRET_KEY'] = 'test-secret-for-routes' # For session, etc.
    # Set placeholder webhook ID for tests
    app.config['PAYPAL_WEBHOOK_ID'] = 'TEST_WEBHOOK_ID'

    with app.app_context():
        db.drop_all()
        db.create_all()
    with app.test_client() as client:
        yield client

@pytest.fixture
def test_user(client):
    """Creates a user and their wallet directly in the DB for testing."""
    with client.application.app_context():
        user = User(phone='+19876543210', email='paypal.test@example.com')
        db.session.add(user)
        db.session.commit()
        
        # Create wallet for this user (manually, as create_profile is not called here)
        # In a real app, create_profile would handle this.
        # For route testing, we often need to set up the state directly.
        from services.wallet_service import create_user_wallet
        wallet = create_user_wallet(user_id=user.id)
        assert wallet is not None
        
        # Mock the get_current_user_id_placeholder to return this user's ID
        # This is a bit of a hack. Better would be to simulate login if auth system was real.
        # For now, we can patch the placeholder function directly in tests that need it.
        user_detail = {'id': user.id, 'wallet_id': wallet.id}
        return user_detail


# --- Helper to set current user for placeholder auth ---
def _set_test_user_id(endpoint_function, user_id):
    """Sets the user ID for the placeholder auth for a given endpoint function."""
    # This relies on the specific implementation of the placeholder in routes_wallet.py
    endpoint_function._user_id_for_test = user_id


# --- Tests for /top-up/paypal/initiate ---

@patch('services.paypal_service.create_payment_order')
@patch('services.wallet_service.create_transaction') # Mock to inspect its call
def test_initiate_paypal_top_up_success(mock_create_internal_tx, mock_create_payment_order, client, test_user):
    # Setup current user for the placeholder auth
    from app.routes_wallet import initiate_paypal_top_up as endpoint_func
    _set_test_user_id(endpoint_func, test_user['id'])

    # Mock internal transaction creation
    mock_internal_tx_instance = MagicMock(spec=Transaction)
    mock_internal_tx_instance.id = 123 # Crucial for url_for
    mock_internal_tx_instance.amount = Decimal('100.00')
    mock_internal_tx_instance.currency = 'ZAR'
    mock_internal_tx_instance.status = 'pending'
    mock_internal_tx_instance.external_transaction_id = None # Initially None
    mock_create_internal_tx.return_value = mock_internal_tx_instance
    
    # Mock PayPal service response
    mock_create_payment_order.return_value = {
        "payment_id": "PAYID-TEST123",
        "approval_url": "http://paypal.com/approve/PAYID-TEST123",
        "error": None
    }

    with client.application.app_context(): # Ensure app context for url_for
        response = client.post(url_for('wallet_routes.initiate_paypal_top_up'), json={'amount': '100.00'})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['approval_url'] == "http://paypal.com/approve/PAYID-TEST123"

    # Verify internal transaction was created with correct initial details
    mock_create_internal_tx.assert_called_once_with(
        wallet_id=test_user['wallet_id'],
        type='deposit',
        amount=Decimal('100.00'),
        currency='ZAR', # From constant in routes_wallet
        status='pending',
        description='PayPal Top-Up Initiation'
    )
    
    # Verify PayPal payment order was called correctly
    expected_approve_url = url_for('wallet_routes.paypal_execute_payment', transaction_id=123, _external=True)
    expected_cancel_url = url_for('wallet_routes.paypal_cancel_payment', transaction_id=123, _external=True)
    mock_create_payment_order.assert_called_once_with(
        total_amount='100.00',
        currency='ZAR',
        return_url_approve=expected_approve_url,
        return_url_cancel=expected_cancel_url
    )
    
    # Verify the mock transaction object (which is returned by our mocked create_transaction)
    # had its external_transaction_id updated.
    # Note: This checks the mock object, not the DB directly, as create_transaction is fully mocked.
    assert mock_internal_tx_instance.external_transaction_id == "PAYID-TEST123"
    # To check db.session.commit() was called on the real db object after this update:
    # This requires a more complex setup or ensuring db.session.commit is also patched if isolating.
    # For now, we assume the route's db.session.commit() works.


@patch('services.paypal_service.create_payment_order')
@patch('services.wallet_service.create_transaction')
def test_initiate_paypal_top_up_paypal_failure(mock_create_internal_tx, mock_create_payment_order, client, test_user):
    from app.routes_wallet import initiate_paypal_top_up as endpoint_func
    _set_test_user_id(endpoint_func, test_user['id'])

    mock_internal_tx_instance = MagicMock(spec=Transaction)
    mock_internal_tx_instance.id = 456
    mock_internal_tx_instance.status = 'pending' # Initial status
    mock_create_internal_tx.return_value = mock_internal_tx_instance

    mock_create_payment_order.return_value = {
        "error": "PayPal system down"
    }

    with client.application.app_context():
        response = client.post(url_for('wallet_routes.initiate_paypal_top_up'), json={'amount': '75.00'})

    assert response.status_code == 500
    json_data = response.get_json()
    assert "Failed to initiate PayPal payment" in json_data['error']
    assert json_data['details'] == "PayPal system down"
    
    # Verify internal transaction status was updated to 'failed'
    assert mock_internal_tx_instance.status == 'failed'
    assert mock_internal_tx_instance.description == "PayPal initiation failed: PayPal system down"


def test_initiate_paypal_top_up_amount_validation(client, test_user):
    from app.routes_wallet import initiate_paypal_top_up as endpoint_func, MIN_TOP_UP, MAX_TOP_UP, TRANSACTION_CURRENCY
    _set_test_user_id(endpoint_func, test_user['id'])

    with client.application.app_context():
        # Below min
        response_min = client.post(url_for('wallet_routes.initiate_paypal_top_up'), json={'amount': str(MIN_TOP_UP - Decimal('1.00'))})
        assert response_min.status_code == 400
        assert f'Amount must be between {MIN_TOP_UP} and {MAX_TOP_UP} {TRANSACTION_CURRENCY}' in response_min.get_json()['error']

        # Above max
        response_max = client.post(url_for('wallet_routes.initiate_paypal_top_up'), json={'amount': str(MAX_TOP_UP + Decimal('1.00'))})
        assert response_max.status_code == 400
        assert f'Amount must be between {MIN_TOP_UP} and {MAX_TOP_UP} {TRANSACTION_CURRENCY}' in response_max.get_json()['error']

        # Invalid format
        response_invalid = client.post(url_for('wallet_routes.initiate_paypal_top_up'), json={'amount': 'not-a-number'})
        assert response_invalid.status_code == 400
        assert 'Invalid amount format' in response_invalid.get_json()['error']

        # Missing amount
        response_missing = client.post(url_for('wallet_routes.initiate_paypal_top_up'), json={})
        assert response_missing.status_code == 400
        assert 'Amount is required' in response_missing.get_json()['error']


def test_initiate_paypal_top_up_no_wallet(client): # Test with a user that has no wallet
    from app.routes_wallet import initiate_paypal_top_up as endpoint_func
    
    # Create a user without a wallet for this specific test
    with client.application.app_context():
        no_wallet_user = User(phone='+1112223333', email='no.wallet@example.com')
        db.session.add(no_wallet_user)
        db.session.commit()
        _set_test_user_id(endpoint_func, no_wallet_user.id)

        response = client.post(url_for('wallet_routes.initiate_paypal_top_up'), json={'amount': '100.00'})
    
    assert response.status_code == 404
    assert response.get_json()['error'] == 'Wallet not found for user'

# --- Tests for /top-up/paypal/execute/<transaction_id> ---

@patch('services.paypal_service.execute_paypal_payment')
def test_execute_paypal_payment_success(mock_execute_paypal, client, test_user):
    from app.routes_wallet import paypal_execute_payment as endpoint_func
    _set_test_user_id(endpoint_func, test_user['id'])

    # Setup: Create a pending transaction
    initial_amount = Decimal('200.00')
    with client.application.app_context():
        pending_tx = Transaction(
            wallet_id=test_user['wallet_id'],
            type='deposit',
            amount=initial_amount,
            currency='ZAR',
            status='pending',
            external_transaction_id='PAYID-EXECUTE-SUCCESS'
        )
        db.session.add(pending_tx)
        db.session.commit()
        tx_id = pending_tx.id
        
        # Get initial wallet balance
        wallet_before = Wallet.query.get(test_user['wallet_id'])
        balance_before = wallet_before.balance

    # Mock PayPal service response
    mock_execute_paypal.return_value = {"success": True, "payment": {"id": "PAYID-EXECUTE-SUCCESS"}}

    response = client.get(url_for('wallet_routes.paypal_execute_payment', transaction_id=tx_id, 
                                  paymentId='PAYID-EXECUTE-SUCCESS', PayerID='PAYERID-TEST'))
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'PayPal top-up successful!'
    
    with client.application.app_context():
        updated_tx = Transaction.query.get(tx_id)
        assert updated_tx.status == 'completed'
        
        wallet_after = Wallet.query.get(test_user['wallet_id'])
        fee_percentage = Decimal('0.15')
        fee_expected = (initial_amount * fee_percentage).quantize(Decimal('0.01'))
        net_amount_expected = initial_amount - fee_expected
        assert wallet_after.balance == balance_before + net_amount_expected
        
        # Verify fee transaction
        fee_tx = Transaction.query.filter_by(wallet_id=test_user['wallet_id'], type='fee').order_by(Transaction.id.desc()).first()
        assert fee_tx is not None
        assert fee_tx.amount == fee_expected
        assert fee_tx.status == 'completed'
        assert f'Processing fee for PayPal top-up (TXN ID: {tx_id})' in fee_tx.description

@patch('services.paypal_service.execute_paypal_payment')
def test_execute_paypal_payment_paypal_failure(mock_execute_paypal, client, test_user):
    from app.routes_wallet import paypal_execute_payment as endpoint_func
    _set_test_user_id(endpoint_func, test_user['id'])

    with client.application.app_context():
        pending_tx = Transaction(wallet_id=test_user['wallet_id'], type='deposit', amount=Decimal('100.00'), currency='ZAR', status='pending', external_transaction_id='PAYID-EXECUTE-FAIL')
        db.session.add(pending_tx)
        db.session.commit()
        tx_id = pending_tx.id
        
    mock_execute_paypal.return_value = {"success": False, "error": "PayPal denied the payment."}

    response = client.get(url_for('wallet_routes.paypal_execute_payment', transaction_id=tx_id, paymentId='PAYID-EXECUTE-FAIL', PayerID='PAYERID-FAIL'))
    
    assert response.status_code == 400
    assert "PayPal payment execution failed" in response.get_json()['error']
    assert "PayPal denied the payment." in response.get_json()['details']
    
    with client.application.app_context():
        failed_tx = Transaction.query.get(tx_id)
        assert failed_tx.status == 'failed'
        assert "PayPal execution failed: PayPal denied the payment." in failed_tx.description


def test_execute_paypal_payment_invalid_tx_status(client, test_user):
    from app.routes_wallet import paypal_execute_payment as endpoint_func
    _set_test_user_id(endpoint_func, test_user['id'])

    with client.application.app_context():
        completed_tx = Transaction(wallet_id=test_user['wallet_id'], type='deposit', amount=Decimal('50.00'), currency='ZAR', status='completed', external_transaction_id='PAYID-COMPLETED')
        db.session.add(completed_tx)
        db.session.commit()
        tx_id = completed_tx.id
        
    response = client.get(url_for('wallet_routes.paypal_execute_payment', transaction_id=tx_id, paymentId='PAYID-COMPLETED', PayerID='PAYERID-STATUS'))
    
    assert response.status_code == 400
    assert "Invalid or already processed transaction" in response.get_json()['error']


# --- Tests for /top-up/paypal/cancel/<transaction_id> ---

def test_cancel_paypal_payment_success(client, test_user):
    from app.routes_wallet import paypal_cancel_payment as endpoint_func
    _set_test_user_id(endpoint_func, test_user['id'])

    with client.application.app_context():
        pending_tx = Transaction(wallet_id=test_user['wallet_id'], type='deposit', amount=Decimal('100.00'), currency='ZAR', status='pending')
        db.session.add(pending_tx)
        db.session.commit()
        tx_id = pending_tx.id

    response = client.get(url_for('wallet_routes.paypal_cancel_payment', transaction_id=tx_id))
    
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Payment cancelled successfully'
    
    with client.application.app_context():
        cancelled_tx = Transaction.query.get(tx_id)
        assert cancelled_tx.status == 'cancelled'
        assert "User cancelled PayPal payment." in cancelled_tx.description

def test_cancel_paypal_payment_invalid_status(client, test_user):
    from app.routes_wallet import paypal_cancel_payment as endpoint_func
    _set_test_user_id(endpoint_func, test_user['id'])

    with client.application.app_context():
        completed_tx = Transaction(wallet_id=test_user['wallet_id'], type='deposit', amount=Decimal('100.00'), currency='ZAR', status='completed')
        db.session.add(completed_tx)
        db.session.commit()
        tx_id = completed_tx.id

    response = client.get(url_for('wallet_routes.paypal_cancel_payment', transaction_id=tx_id))
    
    assert response.status_code == 400
    assert "Transaction already in a final state: completed" in response.get_json()['message']


# --- Tests for /top-up/paypal/webhook ---

@patch('services.paypal_service.verify_webhook_event')
def test_paypal_webhook_sale_completed(mock_verify_webhook, client, test_user):
    # Mock successful webhook verification
    mock_event = MagicMock()
    mock_event.event_type = "PAYMENT.SALE.COMPLETED"
    mock_event.id = "EVT-WEBHOOK-COMPLETED"
    mock_event.resource = MagicMock()
    mock_event.resource.get.return_value = 'PAYID-WEBHOOK-SALE' # parent_payment
    mock_event.resource.id = 'SALEID-WEBHOOK-123' # sale id
    mock_verify_webhook.return_value = mock_event
    
    initial_amount = Decimal("300.00")
    with client.application.app_context():
        # Ensure wallet exists for the test_user
        wallet = Wallet.query.get(test_user['wallet_id'])
        assert wallet is not None
        balance_before = wallet.balance

        # Create a pending transaction that this webhook will complete
        pending_tx = Transaction(
            wallet_id=test_user['wallet_id'], 
            type='deposit', 
            amount=initial_amount, 
            currency='ZAR', 
            status='pending', 
            external_transaction_id='PAYID-WEBHOOK-SALE'
        )
        db.session.add(pending_tx)
        db.session.commit()
        tx_id = pending_tx.id

    # Simulate webhook request
    response = client.post(url_for('wallet_routes.paypal_webhook_listener'), 
                           data="{}", headers={'Content-Type': 'application/json'}) # Body/headers content doesn't matter much due to mocking verify

    assert response.status_code == 200
    assert response.get_json()['status'] == 'received'
    
    mock_verify_webhook.assert_called_once() # Ensure verification was attempted
    
    with client.application.app_context():
        processed_tx = Transaction.query.get(tx_id)
        assert processed_tx.status == 'completed'
        assert f"PayPal payment completed via webhook. Event ID: {mock_event.id}. Sale ID: {mock_event.resource.id}" in processed_tx.description
        
        wallet_after = Wallet.query.get(test_user['wallet_id'])
        fee_percentage = Decimal('0.15')
        fee_expected = (initial_amount * fee_percentage).quantize(Decimal('0.01'))
        net_amount_expected = initial_amount - fee_expected
        assert wallet_after.balance == balance_before + net_amount_expected
        
        # Check for fee transaction idempotency
        fee_tx_external_id = f"{'PAYID-WEBHOOK-SALE'}_fee_wh"
        fee_tx_count = Transaction.query.filter_by(external_transaction_id=fee_tx_external_id).count()
        assert fee_tx_count == 1
        fee_tx = Transaction.query.filter_by(external_transaction_id=fee_tx_external_id).first()
        assert fee_tx.amount == fee_expected

@patch('services.paypal_service.verify_webhook_event')
def test_paypal_webhook_sale_denied(mock_verify_webhook, client, test_user):
    mock_event = MagicMock()
    mock_event.event_type = "PAYMENT.SALE.DENIED"
    mock_event.id = "EVT-WEBHOOK-DENIED"
    mock_event.resource = MagicMock()
    mock_event.resource.get.return_value = 'PAYID-WEBHOOK-DENY'
    mock_event.resource.id = 'SALEID-WEBHOOK-456'
    mock_verify_webhook.return_value = mock_event

    with client.application.app_context():
        pending_tx = Transaction(wallet_id=test_user['wallet_id'], type='deposit', amount=Decimal('50.00'), currency='ZAR', status='pending', external_transaction_id='PAYID-WEBHOOK-DENY')
        db.session.add(pending_tx)
        db.session.commit()
        tx_id = pending_tx.id

    response = client.post(url_for('wallet_routes.paypal_webhook_listener'), data="{}", headers={})
    
    assert response.status_code == 200
    
    with client.application.app_context():
        denied_tx = Transaction.query.get(tx_id)
        assert denied_tx.status == 'failed'
        assert f"PayPal payment denied/failed via webhook. Event ID: {mock_event.id}. Sale ID: {mock_event.resource.id}" in denied_tx.description

@patch('services.paypal_service.verify_webhook_event', return_value=None) # Mock verification failure
def test_paypal_webhook_verification_failure(mock_verify_webhook_failed, client):
    response = client.post(url_for('wallet_routes.paypal_webhook_listener'), data="{}", headers={})
    
    assert response.status_code == 400 # As per current implementation
    assert response.get_json()['status'] == 'verification_failed'
    mock_verify_webhook_failed.assert_called_once()

# --- Tests for /withdrawals/bank ---

def test_withdraw_to_bank_success(client, test_user):
    from app.routes_wallet import withdraw_to_bank as endpoint_func
    _set_test_user_id(endpoint_func, test_user['id'])

    initial_balance = Decimal('1000.00')
    withdrawal_amount_gross = Decimal('100.00')
    
    with client.application.app_context():
        # Set initial wallet balance
        wallet = Wallet.query.get(test_user['wallet_id'])
        wallet.balance = initial_balance
        
        # Create a linked bank account
        bank_details = {"bank_name": "Test Bank", "account_number": "1234567890", "account_holder_name": "Test User"}
        linked_bank = LinkedAccount(user_id=test_user['id'], account_type='bank', account_details=bank_details, is_verified=True) # Assume verified for this test
        db.session.add(linked_bank)
        db.session.commit()
        linked_bank_id = linked_bank.id

    response = client.post(url_for('wallet_routes.withdraw_to_bank'), 
                           json={'amount': str(withdrawal_amount_gross), 'linked_account_id': linked_bank_id})
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'Withdrawal to bank initiated. Pending admin approval.'
    assert Decimal(json_data['amount_debited']) == withdrawal_amount_gross
    
    fee_percentage = Decimal('0.15')
    expected_fee = (withdrawal_amount_gross * fee_percentage).quantize(Decimal('0.01'))
    assert Decimal(json_data['fee_charged']) == expected_fee

    with client.application.app_context():
        wallet_after = Wallet.query.get(test_user['wallet_id'])
        assert wallet_after.balance == initial_balance - withdrawal_amount_gross # Balance debited by gross

        withdrawal_tx = Transaction.query.filter_by(wallet_id=wallet.id, type='withdrawal').first()
        assert withdrawal_tx is not None
        assert withdrawal_tx.status == 'pending_manual'
        assert withdrawal_tx.amount == withdrawal_amount_gross
        
        fee_tx = Transaction.query.filter_by(wallet_id=wallet.id, type='fee', description=f"Fee for bank withdrawal, main TX ID: {withdrawal_tx.id}").first()
        assert fee_tx is not None
        assert fee_tx.status == 'completed'
        assert fee_tx.amount == expected_fee


def test_withdraw_to_bank_insufficient_balance(client, test_user):
    from app.routes_wallet import withdraw_to_bank as endpoint_func
    _set_test_user_id(endpoint_func, test_user['id'])

    with client.application.app_context():
        wallet = Wallet.query.get(test_user['wallet_id'])
        wallet.balance = Decimal('50.00') # Less than withdrawal amount
        bank_details = {"bank_name": "Test Bank", "account_number": "000", "account_holder_name": "Test User"}
        linked_bank = LinkedAccount(user_id=test_user['id'], account_type='bank', account_details=bank_details, is_verified=True)
        db.session.add(linked_bank)
        db.session.commit()
        linked_bank_id = linked_bank.id

    response = client.post(url_for('wallet_routes.withdraw_to_bank'), 
                           json={'amount': '100.00', 'linked_account_id': linked_bank_id})
    
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Insufficient wallet balance.'
    
    with client.application.app_context():
        wallet_after = Wallet.query.get(test_user['wallet_id'])
        assert wallet_after.balance == Decimal('50.00') # Unchanged
        assert Transaction.query.filter_by(wallet_id=wallet.id, type='withdrawal').count() == 0


def test_withdraw_to_bank_invalid_linked_account(client, test_user):
    from app.routes_wallet import withdraw_to_bank as endpoint_func
    _set_test_user_id(endpoint_func, test_user['id'])
    
    # Case 1: Account not found
    response_not_found = client.post(url_for('wallet_routes.withdraw_to_bank'), 
                                     json={'amount': '50.00', 'linked_account_id': 9999})
    assert response_not_found.status_code == 400 # Service returns error dict, route makes it 400
    assert 'Invalid or inaccessible bank account specified' in response_not_found.get_json()['error']

    # Case 2: Account is not 'bank' type
    with client.application.app_context():
        paypal_acc = LinkedAccount(user_id=test_user['id'], account_type='paypal', account_details={"paypal_email":"test@p.com"})
        db.session.add(paypal_acc)
        db.session.commit()
        paypal_acc_id = paypal_acc.id
    
    response_wrong_type = client.post(url_for('wallet_routes.withdraw_to_bank'), 
                                     json={'amount': '50.00', 'linked_account_id': paypal_acc_id})
    assert response_wrong_type.status_code == 400
    assert 'Invalid or inaccessible bank account specified' in response_wrong_type.get_json()['error']


# --- Tests for /withdrawals/paypal ---

@patch('services.paypal_service.create_paypal_payout')
def test_withdraw_to_paypal_success_sync(mock_create_payout, client, test_user):
    from app.routes_wallet import withdraw_to_paypal as endpoint_func
    _set_test_user_id(endpoint_func, test_user['id'])

    initial_balance = Decimal('500.00')
    withdrawal_amount_gross = Decimal('200.00')

    with client.application.app_context():
        wallet = Wallet.query.get(test_user['wallet_id'])
        wallet.balance = initial_balance
        paypal_details = {"paypal_email": "receiver_paypal@example.com"}
        linked_paypal = LinkedAccount(user_id=test_user['id'], account_type='paypal', account_details=paypal_details, is_verified=True)
        db.session.add(linked_paypal)
        db.session.commit()
        linked_paypal_id = linked_paypal.id

    mock_create_payout.return_value = {
        "success": True, 
        "payout_batch_id": "PAYOUT-BATCH-ID-SUCCESS", 
        "details": {"items": [{"transaction_status": "SUCCESS"}]} # Simulate immediate success
    }

    response = client.post(url_for('wallet_routes.withdraw_to_paypal'), 
                           json={'amount': str(withdrawal_amount_gross), 'linked_account_id': linked_paypal_id})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'PayPal withdrawal processed. Status: completed'
    
    fee_percentage = Decimal('0.15')
    expected_fee = (withdrawal_amount_gross * fee_percentage).quantize(Decimal('0.01'))
    net_amount_sent = withdrawal_amount_gross - expected_fee
    assert Decimal(json_data['amount_sent']) == net_amount_sent
    assert Decimal(json_data['fee_charged']) == expected_fee

    mock_create_payout.assert_called_once_with(
        recipient_email="receiver_paypal@example.com",
        amount_value=str(net_amount_sent),
        currency='ZAR',
        internal_payout_id=str(Transaction.query.filter_by(wallet_id=wallet.id, type='withdrawal').first().id) # Fragile if other TX exist
    )

    with client.application.app_context():
        wallet_after = Wallet.query.get(test_user['wallet_id'])
        assert wallet_after.balance == initial_balance - withdrawal_amount_gross

        withdrawal_tx = Transaction.query.filter_by(wallet_id=wallet.id, type='withdrawal').first()
        assert withdrawal_tx.status == 'completed'
        assert withdrawal_tx.external_transaction_id == "PAYOUT-BATCH-ID-SUCCESS"
        
        fee_tx = Transaction.query.filter_by(wallet_id=wallet.id, type='fee').first()
        assert fee_tx.status == 'completed'
        assert fee_tx.amount == expected_fee


@patch('services.paypal_service.create_paypal_payout')
def test_withdraw_to_paypal_payout_api_failure(mock_create_payout, client, test_user):
    from app.routes_wallet import withdraw_to_paypal as endpoint_func
    _set_test_user_id(endpoint_func, test_user['id'])

    initial_balance = Decimal('300.00')
    with client.application.app_context():
        wallet = Wallet.query.get(test_user['wallet_id'])
        wallet.balance = initial_balance
        paypal_details = {"paypal_email": "fail_receiver@example.com"}
        linked_paypal = LinkedAccount(user_id=test_user['id'], account_type='paypal', account_details=paypal_details, is_verified=True)
        db.session.add(linked_paypal)
        db.session.commit()
        linked_paypal_id = linked_paypal.id

    mock_create_payout.return_value = {"success": False, "error": "PayPal API Error"}

    response = client.post(url_for('wallet_routes.withdraw_to_paypal'), 
                           json={'amount': '100.00', 'linked_account_id': linked_paypal_id})

    assert response.status_code == 500 # Or 400 depending on how you classify API errors from PayPal
    json_data = response.get_json()
    assert "PayPal Payout failed" in json_data['error']
    assert "PayPal API Error" in json_data['details']

    with client.application.app_context():
        wallet_after = Wallet.query.get(test_user['wallet_id'])
        assert wallet_after.balance == initial_balance # Balance rolled back

        withdrawal_tx = Transaction.query.filter_by(wallet_id=wallet.id, type='withdrawal').first()
        assert withdrawal_tx.status == 'failed'
        assert "PayPal Payout API call failed: PayPal API Error" in withdrawal_tx.description
        
        fee_tx = Transaction.query.filter_by(wallet_id=wallet.id, type='fee').first()
        assert fee_tx.status == 'cancelled' # Fee cancelled due to payout failure

def test_withdraw_to_paypal_insufficient_balance(client, test_user):
    from app.routes_wallet import withdraw_to_paypal as endpoint_func
    _set_test_user_id(endpoint_func, test_user['id'])

    with client.application.app_context():
        wallet = Wallet.query.get(test_user['wallet_id'])
        wallet.balance = Decimal('10.00') # Gross withdrawal will be more due to fees
        paypal_details = {"paypal_email": "low_bal@example.com"}
        linked_paypal = LinkedAccount(user_id=test_user['id'], account_type='paypal', account_details=paypal_details, is_verified=True)
        db.session.add(linked_paypal)
        db.session.commit()
        linked_paypal_id = linked_paypal.id

    response = client.post(url_for('wallet_routes.withdraw_to_paypal'), 
                           json={'amount': '10.00', 'linked_account_id': linked_paypal_id})
    
    # Example: 10.00 ZAR. Fee is 1.50. Net is 8.50. Gross needed is 10.00.
    # If amount is the gross withdrawal:
    # Gross = 10.00, Fee = 1.50, Net = 8.50. Wallet balance must be >= 10.00
    # If wallet.balance is 10.00, this should pass for gross=10.
    # If wallet.balance is 5.00, and gross=10.00, this should fail.
    # Let's test with balance < gross_withdrawal_amount
    
    # If wallet.balance = 10, and user tries to withdraw amount=20 (gross)
    wallet = Wallet.query.get(test_user['wallet_id'])
    wallet.balance = Decimal('10.00')
    db.session.commit()

    response_insufficient = client.post(url_for('wallet_routes.withdraw_to_paypal'), 
                           json={'amount': '20.00', 'linked_account_id': linked_paypal_id})

    assert response_insufficient.status_code == 400
    assert response_insufficient.get_json()['error'] == 'Insufficient wallet balance.'
```
