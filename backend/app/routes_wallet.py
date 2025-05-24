from flask import Blueprint, request, jsonify, url_for, current_app
from decimal import Decimal, InvalidOperation

# Assuming a decorator like @jwt_required or similar. For now, a placeholder.
import logging # Added for webhook logging
from flask import Blueprint, request, jsonify, url_for, current_app
from decimal import Decimal, InvalidOperation

# from flask_jwt_extended import jwt_required, get_jwt_identity # Example
from functools import wraps # For creating a placeholder decorator

from app.models import User 
from app.wallet import Wallet, Transaction, LinkedAccount 
from app.db import db
from services.wallet_service import create_transaction
from services.paypal_service import (
    create_payment_order, 
    execute_paypal_payment, 
    verify_webhook_event,
    create_paypal_payout # Added for PayPal withdrawal
)
# Import linked account services
from services.linked_account_service import (
    add_linked_account,
    get_linked_accounts_for_user,
    get_linked_account_by_id,
    remove_linked_account
)

wallet_bp = Blueprint('wallet_routes', __name__)

# --- Placeholder for Authentication ---
# This is a simplified placeholder. In a real app, this would use JWT, Flask-Login, etc.
def login_required_placeholder(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Simulate getting user_id from a token or session
        # For testing, we might hardcode a user_id or use a header
        # g.user_id = request.headers.get('X-User-Id', 1) # Example: get from header or default
        if not hasattr(decorated_function, '_user_id_for_test'):
            decorated_function._user_id_for_test = 1 # Default test user_id if not set by test
        return f(*args, **kwargs)
    return decorated_function

def get_current_user_id_placeholder():
    # In a real app, this would come from g.user_id, get_jwt_identity(), current_user.id, etc.
    # For now, using the value set by the placeholder decorator or a default.
    # This is NOT production-safe.
    if hasattr(initiate_paypal_top_up, '_user_id_for_test'):
         return initiate_paypal_top_up._user_id_for_test
    return 1 # Default if not set by test directly on the endpoint function

# --- Constants ---
MIN_TOP_UP = Decimal('50.00')
MAX_TOP_UP = Decimal('25000.00')
TRANSACTION_CURRENCY = 'ZAR'


# --- Placeholder routes for url_for ---
@wallet_bp.route('/top-up/paypal/execute/<int:transaction_id>', methods=['GET'])
@login_required_placeholder 
def paypal_execute_payment(transaction_id):
    user_id = get_current_user_id_placeholder() # Get current user ID (placeholder)

    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')

    if not payment_id or not payer_id:
        return jsonify({'error': 'Missing paymentId or PayerID from PayPal redirect'}), 400

    our_tx = Transaction.query.get(transaction_id)

    if not our_tx:
        return jsonify({'error': 'Transaction not found'}), 404
    
    # Security check: Ensure the transaction belongs to the logged-in user
    wallet_owner = Wallet.query.get(our_tx.wallet_id)
    if not wallet_owner or wallet_owner.user_id != user_id:
        return jsonify({'error': 'Transaction does not belong to the current user'}), 403


    if our_tx.status != 'pending':
        return jsonify({'error': 'Invalid or already processed transaction', 'status': our_tx.status}), 400

    paypal_response = execute_paypal_payment(payment_id, payer_id)

    if paypal_response.get("success"):
        our_tx.status = 'completed'
        # PayPal payment ID might be different from the one initially stored if using newer APIs,
        # but for classic REST API, payment.id from create is the same as paymentId on execute.
        # Confirming/updating external_transaction_id if necessary.
        our_tx.external_transaction_id = payment_id 
        
        wallet = Wallet.query.get(our_tx.wallet_id)
        if not wallet: # Should not happen if our_tx exists and is valid
            our_tx.status = 'failed'
            our_tx.description = "Critical error: Wallet not found during execution."
            db.session.commit()
            return jsonify({'error': 'Wallet associated with transaction not found'}), 500

        gross_amount = our_tx.amount # This is the amount the user intended to top-up
        
        # Fee Calculation (15% as per example)
        # Ensure this is clearly communicated to the user beforehand
        fee_percentage = Decimal('0.15') 
        fee = (gross_amount * fee_percentage).quantize(Decimal('0.01')) # Standard rounding for currency
        net_amount = gross_amount - fee
        
        if net_amount < Decimal('0.00'): # Should not happen with positive gross_amount
            net_amount = Decimal('0.00')

        wallet.balance += net_amount
        
        # Create a separate transaction for the fee
        create_transaction(
            wallet_id=wallet.id,
            type='fee',
            amount=fee, # Fee amount is positive
            currency=our_tx.currency,
            status='completed',
            description=f'Processing fee for PayPal top-up (TXN ID: {our_tx.id})',
            # external_transaction_id might be linked to the original paymentId or internal ref
        )
        
        db.session.commit()
        # TODO: Send user notification of successful top-up
        current_app.logger.info(f"User {user_id} successfully topped up wallet {wallet.id} by {net_amount} {our_tx.currency} (Gross: {gross_amount}, Fee: {fee}). PayPal Payment ID: {payment_id}")
        return jsonify({
            'message': 'PayPal top-up successful!', 
            'net_amount_credited': str(net_amount),
            'gross_amount': str(gross_amount),
            'fee_applied': str(fee),
            'currency': our_tx.currency
        }), 200
    else:
        our_tx.status = 'failed'
        error_detail = paypal_response.get('error', 'Unknown error from PayPal service')
        our_tx.description = f"PayPal execution failed: {error_detail}"
        db.session.commit()
        # TODO: Send user notification of failed top-up
        current_app.logger.error(f"User {user_id} PayPal top-up failed for TXN ID {our_tx.id}. PayPal Payment ID: {payment_id}. Error: {error_detail}")
        return jsonify({'error': 'PayPal payment execution failed', 'details': error_detail}), 400

@wallet_bp.route('/top-up/paypal/cancel/<int:transaction_id>', methods=['GET'])
@login_required_placeholder
def paypal_cancel_payment(transaction_id):
    user_id = get_current_user_id_placeholder() # Get current user ID (placeholder)
    our_tx = Transaction.query.get(transaction_id)

    if not our_tx:
        return jsonify({'error': 'Transaction not found'}), 404

    # Security check: Ensure the transaction belongs to the logged-in user
    wallet_owner = Wallet.query.get(our_tx.wallet_id)
    if not wallet_owner or wallet_owner.user_id != user_id:
        return jsonify({'error': 'Transaction does not belong to the current user'}), 403

    if our_tx.status == 'pending':
        our_tx.status = 'cancelled'
        our_tx.description = "User cancelled PayPal payment."
        db.session.commit()
        current_app.logger.info(f"User {user_id} cancelled PayPal top-up for TXN ID {our_tx.id}.")
        return jsonify({'message': 'Payment cancelled successfully'}), 200
    elif our_tx.status in ['completed', 'failed', 'cancelled']:
        return jsonify({'message': f'Transaction already in a final state: {our_tx.status}'}), 400
    else: # Other statuses that might not be final but aren't 'pending'
        return jsonify({'message': 'Transaction in a non-cancellable state'}), 400


@wallet_bp.route('/top-up/paypal/initiate', methods=['POST'])
@login_required_placeholder # Apply your actual login decorator here
def initiate_paypal_top_up():
    user_id = get_current_user_id_placeholder() # Placeholder for actual current_user.id

    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        return jsonify({'error': 'Wallet not found for user'}), 404

    amount_str = request.json.get('amount')
    if not amount_str:
        return jsonify({'error': 'Amount is required'}), 400

    try:
        gross_amount = Decimal(amount_str)
    except InvalidOperation:
        return jsonify({'error': 'Invalid amount format. Must be a valid number.'}), 400

    if not (MIN_TOP_UP <= gross_amount <= MAX_TOP_UP):
        return jsonify({'error': f'Amount must be between {MIN_TOP_UP} and {MAX_TOP_UP} {TRANSACTION_CURRENCY}.'}), 400

    # Create Internal Pending Transaction
    pending_tx = create_transaction(
        wallet_id=wallet.id,
        type='deposit',
        amount=gross_amount,
        currency=TRANSACTION_CURRENCY,
        status='pending',
        description='PayPal Top-Up Initiation'
    )

    if pending_tx is None:
        # This indicates an issue within create_transaction service (e.g., DB error)
        return jsonify({'error': 'Failed to create internal transaction record'}), 500

    # Prepare PayPal URLs
    try:
        return_url_approve = url_for('wallet_routes.paypal_execute_payment', transaction_id=pending_tx.id, _external=True)
        return_url_cancel = url_for('wallet_routes.paypal_cancel_payment', transaction_id=pending_tx.id, _external=True)
    except Exception as e:
        current_app.logger.error(f"Error generating PayPal return URLs: {e}")
        # Update transaction to failed as we can't proceed
        pending_tx.status = 'failed'
        pending_tx.description = f"URL generation failed: {str(e)}"
        db.session.commit()
        return jsonify({'error': 'Failed to generate PayPal return URLs'}), 500
        
    # Call PayPal Service
    paypal_response = create_payment_order(
        total_amount=str(gross_amount), # PayPal SDK expects string
        currency=TRANSACTION_CURRENCY,
        return_url_approve=return_url_approve,
        return_url_cancel=return_url_cancel
    )

    # Handle PayPal Response
    if paypal_response.get('error') or not paypal_response.get('approval_url'):
        error_detail = paypal_response.get('error', 'Unknown error from PayPal service')
        pending_tx.status = 'failed'
        pending_tx.description = f"PayPal initiation failed: {error_detail}"
        db.session.commit()
        return jsonify({'error': 'Failed to initiate PayPal payment', 'details': error_detail}), 500
    else:
        pending_tx.external_transaction_id = paypal_response['payment_id']
        # Status remains 'pending' until execution or cancellation
        db.session.commit()
        return jsonify({'approval_url': paypal_response['approval_url']}), 200


@wallet_bp.route('/top-up/paypal/webhook', methods=['POST'])
def paypal_webhook_listener():
    expected_webhook_id = current_app.config.get('PAYPAL_WEBHOOK_ID')
    if not expected_webhook_id:
        logging.error("PayPal Webhook: PAYPAL_WEBHOOK_ID is not configured.")
        # Return 200 to PayPal to prevent retries for config errors on our side,
        # but log it as a critical server-side issue.
        return jsonify({'status': 'error', 'message': 'Webhook processing configuration error.'}), 200

    # Get raw body and headers
    raw_body = request.data.decode('utf-8')
    headers = dict(request.headers) # Convert Werkzeug headers to dict

    event = verify_webhook_event(raw_body, headers, expected_webhook_id)

    if not event:
        logging.warning("PayPal Webhook: Verification failed or PAYPAL_WEBHOOK_ID not set properly.")
        # For security reasons, if verification fails, we should not give too much info.
        # A 400 Bad Request might be appropriate if it's clearly a malformed/unverified request.
        # However, PayPal might retry on non-200, so a 200 with logged error is safer to avoid DDOS by retry.
        return jsonify({'status': 'verification_failed'}), 400 # Or 200 with internal logging

    event_type = event.event_type
    resource = event.resource # This is a paypalrestsdk.Resource object
    
    logging.info(f"PayPal Webhook: Received event_type: {event_type}, Event ID: {event.id}")

    # It's crucial to correctly extract the relevant payment/sale ID from the resource.
    # For PAYMENT.SALE.COMPLETED, the sale ID is typically in resource.id,
    # and parent_payment is the original payment ID.
    # We stored parent_payment as external_transaction_id.
    
    payment_id = resource.get('parent_payment') # For sale events
    if not payment_id and hasattr(resource, 'id'): # Fallback for other event types if structure differs
        payment_id = resource.id


    if not payment_id:
        logging.error(f"PayPal Webhook: Could not determine payment_id from resource for event {event.id}. Resource: {resource.to_dict()}")
        return jsonify({'status': 'error', 'message': 'Could not extract payment identifier from webhook.'}), 200


    if event_type == "PAYMENT.SALE.COMPLETED":
        our_tx = Transaction.query.filter_by(external_transaction_id=payment_id).first()

        if our_tx:
            if our_tx.status == 'pending': # Process only if still pending
                our_tx.status = 'completed'
                # Update description to reflect webhook confirmation
                our_tx.description = f"PayPal payment completed via webhook. Event ID: {event.id}. Sale ID: {resource.id if hasattr(resource, 'id') else 'N/A'}"
                
                wallet = Wallet.query.get(our_tx.wallet_id)
                if wallet:
                    gross_amount = our_tx.amount
                    fee_percentage = Decimal('0.15')
                    fee = (gross_amount * fee_percentage).quantize(Decimal('0.01'))
                    net_amount = gross_amount - fee
                    
                    if net_amount < Decimal('0.00'): net_amount = Decimal('0.00')

                    wallet.balance += net_amount
                    
                    # Idempotency check for fee transaction
                    fee_tx_external_id = f"{payment_id}_fee_wh" # Ensure unique ID for webhook fee
                    existing_fee_tx = Transaction.query.filter_by(external_transaction_id=fee_tx_external_id).first()
                    if not existing_fee_tx:
                        create_transaction(
                            wallet_id=wallet.id, 
                            type='fee', 
                            amount=fee, 
                            currency=our_tx.currency, 
                            status='completed', 
                            description=f"Fee for PayPal deposit (Webhook - Sale: {resource.id if hasattr(resource, 'id') else 'N/A'})",
                            external_transaction_id=fee_tx_external_id
                        )
                    else:
                        logging.info(f"PayPal Webhook: Fee transaction {fee_tx_external_id} already exists for {payment_id}.")
                        
                    db.session.commit()
                    logging.info(f"PayPal Webhook: Processed PAYMENT.SALE.COMPLETED for payment_id {payment_id}, transaction_id {our_tx.id}. Wallet {wallet.id} balance updated.")
                    # (TODO: Send user notification if not already handled by execute flow)
                else:
                    logging.error(f"PayPal Webhook: Wallet not found for transaction_id {our_tx.id} during PAYMENT.SALE.COMPLETED processing.")
                    # Transaction status is still 'completed' as PayPal confirmed, but wallet update failed. Needs monitoring.
                    db.session.commit() # Commit transaction status update at least
            else:
                 logging.info(f"PayPal Webhook: Received PAYMENT.SALE.COMPLETED for {payment_id}, but transaction {our_tx.id} was already in status '{our_tx.status}'. No action taken.")
        else:
            logging.warning(f"PayPal Webhook: Received PAYMENT.SALE.COMPLETED for {payment_id} but no matching transaction found with this external_transaction_id.")

    elif event_type == "PAYMENT.SALE.DENIED": # Or other failure types like PAYMENT.SALE.REFUNDED, PAYMENT.SALE.REVERSED
        our_tx = Transaction.query.filter_by(external_transaction_id=payment_id).first()
        if our_tx:
            if our_tx.status == 'pending': # Only update if it was pending
                our_tx.status = 'failed'
                our_tx.description = f"PayPal payment denied/failed via webhook. Event ID: {event.id}. Sale ID: {resource.id if hasattr(resource, 'id') else 'N/A'}"
                db.session.commit()
                logging.info(f"PayPal Webhook: Processed {event_type} for payment_id {payment_id}, transaction_id {our_tx.id} status updated to 'failed'.")
            else:
                logging.info(f"PayPal Webhook: Received {event_type} for {payment_id}, but transaction {our_tx.id} was already in status '{our_tx.status}'. No action taken.")
        else:
            logging.warning(f"PayPal Webhook: Received {event_type} for {payment_id} but no matching transaction found.")
            
    else:
        logging.info(f"PayPal Webhook: Received unhandled event_type: {event_type}. Event ID: {event.id}")

    return jsonify({'status': 'received'}), 200


# --- Linked Account CRUD Endpoints ---

@wallet_bp.route('/linked-accounts', methods=['POST'])
@login_required_placeholder
def handle_add_linked_account():
    user_id = get_current_user_id_placeholder()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    account_type = data.get('account_type')
    account_details = data.get('account_details')
    friendly_name = data.get('friendly_name') # Optional

    if not account_type or not account_details:
        return jsonify({"error": "Missing required fields: account_type and account_details"}), 400

    result = add_linked_account(
        user_id=user_id,
        account_type=account_type,
        account_details=account_details,
        friendly_name=friendly_name
    )

    if isinstance(result, LinkedAccount): # Success if service returns the ORM object
        return jsonify(result.to_dict()), 201
    elif isinstance(result, dict) and 'error' in result: # Error dictionary from service
        # Determine appropriate status code based on error type if possible
        # For now, using 400 for most validation/business logic errors from service
        return jsonify(result), 400 
    else:
        # Should not happen if service always returns ORM object or error dict
        return jsonify({"error": "An unexpected error occurred"}), 500


@wallet_bp.route('/linked-accounts', methods=['GET'])
@login_required_placeholder
def handle_get_linked_accounts():
    user_id = get_current_user_id_placeholder()
    accounts = get_linked_accounts_for_user(user_id)
    return jsonify([acc.to_dict() for acc in accounts]), 200


@wallet_bp.route('/linked-accounts/<int:account_id>', methods=['GET'])
@login_required_placeholder
def handle_get_linked_account_detail(account_id):
    user_id = get_current_user_id_placeholder()
    account = get_linked_account_by_id(account_id, user_id)
    if account:
        return jsonify(account.to_dict()), 200
    else:
        return jsonify({'error': 'Account not found or access denied'}), 404


@wallet_bp.route('/linked-accounts/<int:account_id>', methods=['DELETE'])
@login_required_placeholder
def handle_delete_linked_account(account_id):
    user_id = get_current_user_id_placeholder()
    result = remove_linked_account(account_id, user_id)
    
    if isinstance(result, dict) and result.get('success'):
        return jsonify({'message': 'Account removed successfully'}), 200
    elif isinstance(result, dict) and 'error' in result:
        # Service returns {"error": "Account not found or access denied."} which is suitable for 404
        return jsonify(result), 404 
    else:
        # Should not happen
        return jsonify({"error": "An unexpected error occurred during deletion"}), 500


# --- Withdrawal Endpoints ---

@wallet_bp.route('/withdrawals/bank', methods=['POST'])
@login_required_placeholder
def withdraw_to_bank():
    user_id = get_current_user_id_placeholder()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    amount_str = data.get('amount')
    linked_account_id = data.get('linked_account_id')

    if not amount_str or not linked_account_id:
        return jsonify({"error": "Missing required fields: amount and linked_account_id"}), 400

    # Fetch user's wallet
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        return jsonify({'error': 'Wallet not found for user'}), 404

    # Fetch and validate linked account
    try:
        linked_account_id = int(linked_account_id)
    except ValueError:
        return jsonify({'error': 'Invalid linked_account_id format.'}), 400
        
    linked_account = get_linked_account_by_id(linked_account_id, user_id)
    if not linked_account or linked_account.account_type != 'bank':
        return jsonify({'error': 'Invalid or inaccessible bank account specified.'}), 400
    
    # Optional: Check if bank account is verified (assuming an `is_verified` field exists)
    # if not linked_account.is_verified:
    #     return jsonify({'error': 'Bank account is not verified.'}), 400

    # Validate amount and balance
    try:
        gross_withdrawal_amount = Decimal(amount_str)
    except InvalidOperation:
        return jsonify({'error': 'Invalid amount format. Must be a valid number.'}), 400

    if gross_withdrawal_amount <= Decimal('0.00'):
        return jsonify({'error': 'Withdrawal amount must be positive.'}), 400

    fee_percentage = Decimal('0.15') # 15% withdrawal fee
    withdrawal_fee = (gross_withdrawal_amount * fee_percentage).quantize(Decimal('0.01')) # Standard rounding for currency
    net_amount_user_receives = gross_withdrawal_amount - withdrawal_fee 
    # The total amount debited from wallet is gross_withdrawal_amount

    if wallet.balance < gross_withdrawal_amount:
        return jsonify({'error': 'Insufficient wallet balance.'}), 400

    # Process Withdrawal
    original_balance = wallet.balance
    wallet.balance -= gross_withdrawal_amount
    
    # Construct description
    acc_details = linked_account.account_details
    acc_num_suffix = acc_details.get('account_number', '----')[-4:]
    bank_name_display = acc_details.get('bank_name', 'N/A')
    withdrawal_tx_desc = (
        f"Bank withdrawal to {bank_name_display} Acc ending ****{acc_num_suffix}. "
        f"User receives {net_amount_user_receives:.2f} {TRANSACTION_CURRENCY} after {withdrawal_fee:.2f} {TRANSACTION_CURRENCY} fee."
    )

    withdrawal_tx = create_transaction(
        wallet_id=wallet.id, 
        type='withdrawal', 
        amount=gross_withdrawal_amount, 
        currency=TRANSACTION_CURRENCY, 
        status='pending_manual', 
        description=withdrawal_tx_desc
    )

    if not withdrawal_tx:
        wallet.balance = original_balance # Rollback balance change
        # db.session.commit() # No, don't commit here, let a higher level handle or just log
        logging.error(f"Failed to create withdrawal transaction for user {user_id}, amount {gross_withdrawal_amount}.")
        return jsonify({'error': 'Failed to create withdrawal transaction.'}), 500

    fee_tx = create_transaction(
        wallet_id=wallet.id, 
        type='fee', 
        amount=withdrawal_fee, 
        currency=TRANSACTION_CURRENCY, 
        status='completed', 
        description=f"Fee for bank withdrawal, main TX ID: {withdrawal_tx.id}"
    )

    if not fee_tx:
        # Rollback: an alternative to full rollback is to mark withdrawal_tx as failed
        # For now, we'll try to rollback everything by not committing and returning error
        # This is complex without a full transaction manager or Unit of Work pattern
        wallet.balance = original_balance 
        # If withdrawal_tx was already added to session by its create_transaction, need to expunge or rollback session
        # For simplicity here, we assume create_transaction commits itself, which makes this tricky.
        # A better create_transaction would take a session and not commit.
        # Given current create_transaction likely commits, we'd mark withdrawal_tx as failed.
        # However, the prompt implies sequential commits. If create_transaction commits,
        # then we can't easily roll back withdrawal_tx.
        # Let's assume create_transaction does NOT commit itself for this rollback to make sense.
        # If it does commit, then this rollback is partial and problematic.
        # Re-checking create_transaction: it *does* commit.
        # So, if fee_tx fails, withdrawal_tx is already committed.
        # We should then mark withdrawal_tx as requiring attention or failed.
        
        # Simplified: Log critical error. Manual intervention would be needed if fee_tx fails after withdrawal_tx.
        logging.critical(f"CRITICAL: Failed to create fee transaction for withdrawal {withdrawal_tx.id} for user {user_id}. Withdrawal TX created, balance debited, but fee TX failed.")
        # To prevent user fund loss, we might try to reverse the balance debit here if possible,
        # or ensure the withdrawal_tx is marked as 'failed_fee_missing'.
        # For this task, we'll proceed with the assumption that if fee_tx fails, we report error,
        # but withdrawal_tx might already be 'pending_manual' and balance debited.
        # This highlights need for atomic operations.
        # For now:
        withdrawal_tx.status = 'failed' # Mark original TX as failed due to fee issue
        withdrawal_tx.description += " Fee creation failed."
        wallet.balance = original_balance # Attempt to restore balance
        db.session.add(withdrawal_tx) # Add to session if not already (depends on create_transaction)
        db.session.commit() # Commit the "failed" status and balance restoration
        return jsonify({'error': 'Failed to create fee transaction. Withdrawal rolled back or marked as failed.'}), 500

    try:
        db.session.commit() # Commit wallet balance update, and new transactions if not committed by create_transaction
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error committing withdrawal and fee transactions for user {user_id}: {e}")
        return jsonify({'error': 'Failed to finalize withdrawal process.'}), 500
        
    logging.info(
        f"Admin Notification: User {user_id} initiated bank withdrawal {withdrawal_tx.id} "
        f"for {gross_withdrawal_amount:.2f} {TRANSACTION_CURRENCY} to Account ID {linked_account_id}. "
        f"Net to user: {net_amount_user_receives:.2f} {TRANSACTION_CURRENCY}. Manual processing required."
    )

    return jsonify({
        'message': 'Withdrawal to bank initiated. Pending admin approval.', 
        'transaction_id': withdrawal_tx.id, 
        'amount_debited': str(gross_withdrawal_amount), 
        'fee_charged': str(withdrawal_fee)
    }), 200


@wallet_bp.route('/withdrawals/paypal', methods=['POST'])
@login_required_placeholder
def withdraw_to_paypal():
    user_id = get_current_user_id_placeholder()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    amount_str = data.get('amount')
    linked_account_id = data.get('linked_account_id')

    if not amount_str or not linked_account_id:
        return jsonify({"error": "Missing required fields: amount and linked_account_id"}), 400

    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        return jsonify({'error': 'Wallet not found for user'}), 404

    try:
        linked_account_id = int(linked_account_id)
    except ValueError:
        return jsonify({'error': 'Invalid linked_account_id format.'}), 400
        
    linked_account = get_linked_account_by_id(linked_account_id, user_id)
    if not linked_account or linked_account.account_type != 'paypal':
        return jsonify({'error': 'Invalid or inaccessible PayPal account specified.'}), 400
    
    paypal_email = linked_account.account_details.get('paypal_email')
    if not paypal_email: # Should have been validated when adding linked account
        return jsonify({'error': 'PayPal email not found for the linked account.'}), 400

    try:
        gross_withdrawal_amount = Decimal(amount_str)
    except InvalidOperation:
        return jsonify({'error': 'Invalid amount format. Must be a valid number.'}), 400

    if gross_withdrawal_amount <= Decimal('0.00'):
        return jsonify({'error': 'Withdrawal amount must be positive.'}), 400

    fee_percentage = Decimal('0.15') 
    withdrawal_fee = (gross_withdrawal_amount * fee_percentage).quantize(Decimal('0.01'))
    net_amount_to_send_via_paypal = gross_withdrawal_amount - withdrawal_fee

    if net_amount_to_send_via_paypal <= Decimal('0.00'):
        # This implies the fee is >= 100% of the withdrawal, or amount was too small.
        return jsonify({'error': 'Withdrawal amount too small after fees.'}), 400

    if wallet.balance < gross_withdrawal_amount:
        return jsonify({'error': 'Insufficient wallet balance.'}), 400

    # --- Transaction Handling & Payout Call ---
    original_balance = wallet.balance
    wallet.balance -= gross_withdrawal_amount # Optimistic debit

    withdrawal_tx_desc = (
        f"PayPal withdrawal to {paypal_email}. User receives {net_amount_to_send_via_paypal:.2f} {TRANSACTION_CURRENCY} "
        f"after {withdrawal_fee:.2f} {TRANSACTION_CURRENCY} fee. Gross: {gross_withdrawal_amount:.2f} {TRANSACTION_CURRENCY}."
    )
    
    # Create the main withdrawal transaction, initially 'processing_payout'
    withdrawal_tx = create_transaction(
        wallet_id=wallet.id, 
        type='withdrawal', 
        amount=gross_withdrawal_amount, 
        currency=TRANSACTION_CURRENCY, 
        status='processing_payout', # Status indicating it's being sent to PayPal
        description=withdrawal_tx_desc
    )

    if not withdrawal_tx:
        wallet.balance = original_balance # Rollback optimistic debit
        db.session.commit() # Commit balance restoration
        logging.error(f"PayPal Withdrawal: Failed to create initial withdrawal transaction for user {user_id}, amount {gross_withdrawal_amount}.")
        return jsonify({'error': 'Failed to create withdrawal transaction record.'}), 500

    # Create the fee transaction
    fee_tx = create_transaction(
        wallet_id=wallet.id, 
        type='fee', 
        amount=withdrawal_fee, 
        currency=TRANSACTION_CURRENCY, 
        status='completed', # Fee is charged regardless of payout success for now
        description=f"Fee for PayPal withdrawal, main TX ID: {withdrawal_tx.id}"
    )

    if not fee_tx:
        wallet.balance = original_balance # Rollback optimistic debit
        withdrawal_tx.status = 'failed' # Mark main TX as failed
        withdrawal_tx.description += " Fee creation failed."
        # Note: create_transaction commits. If withdrawal_tx was committed, this updates it.
        db.session.commit() # Commit changes to balance and withdrawal_tx
        logging.error(f"PayPal Withdrawal: Failed to create fee transaction for user {user_id}, withdrawal_tx_id {withdrawal_tx.id}.")
        return jsonify({'error': 'Failed to create fee transaction record.'}), 500

    # At this point, balance is debited, withdrawal_tx and fee_tx are created (and committed by create_transaction)
    # Now, attempt the PayPal Payout
    payout_response = create_paypal_payout(
        recipient_email=paypal_email,
        amount_value=str(net_amount_to_send_via_paypal), # Send the net amount
        currency=TRANSACTION_CURRENCY,
        internal_payout_id=str(withdrawal_tx.id) # Use our transaction ID as internal_payout_id
    )

    if payout_response.get("success"):
        paypal_batch_id = payout_response.get("payout_batch_id")
        withdrawal_tx.external_transaction_id = paypal_batch_id
        
        # Inspect payout details for status (assuming sync_mode=True gives some immediate status)
        # For Payouts, item status is in payout.items[0].transaction_status
        payout_details = payout_response.get("details", {})
        item_status = None
        if payout_details.get("items") and isinstance(payout_details["items"], list) and len(payout_details["items"]) > 0:
            item_status = payout_details["items"][0].get("transaction_status")

        if item_status == 'SUCCESS':
            withdrawal_tx.status = 'completed'
            logging.info(f"PayPal Payout successful (sync) for user {user_id}, TX_ID {withdrawal_tx.id}, Batch ID {paypal_batch_id}")
        elif item_status in ['PENDING', 'UNCLAIMED']: # Unclaimed means recipient needs to accept
            withdrawal_tx.status = 'pending_paypal_confirmation' # Or 'pending_recipient_action'
            withdrawal_tx.description += f" PayPal Payout status: {item_status}."
            logging.info(f"PayPal Payout {item_status} (sync) for user {user_id}, TX_ID {withdrawal_tx.id}, Batch ID {paypal_batch_id}")
        else: # FAILED, BLOCKED, REFUNDED, RETURNED, REVERSED, or other non-success status
            withdrawal_tx.status = 'failed'
            withdrawal_tx.description += f" PayPal Payout status: {item_status or 'UNKNOWN'}. Error: {payout_details.get('items',[{}])[0].get('error',{}).get('message','N/A')}."
            logging.error(f"PayPal Payout failed (sync) for user {user_id}, TX_ID {withdrawal_tx.id}, Batch ID {paypal_batch_id}. Item Status: {item_status}")
            # Note: Funds were already debited. If payout fails terminally here, manual refund/reconciliation might be needed
            # or a subsequent webhook might clarify. For now, marking as 'failed'.

        db.session.commit()
        return jsonify({
            'message': f'PayPal withdrawal processed. Status: {withdrawal_tx.status}', 
            'transaction_id': withdrawal_tx.id,
            'paypal_batch_id': paypal_batch_id,
            'amount_sent': str(net_amount_to_send_via_paypal),
            'fee_charged': str(withdrawal_fee)
        }), 200
    else:
        # Payout API call itself failed (e.g., auth, validation, network)
        wallet.balance = original_balance # Rollback optimistic debit
        withdrawal_tx.status = 'failed'
        withdrawal_tx.description += f" PayPal Payout API call failed: {payout_response.get('error')}"
        
        # Mark fee_tx as cancelled because main operation failed pre-send
        if fee_tx: # Should exist if we reached here
            fee_tx.status = 'cancelled' 
            fee_tx.description = "Cancelled due to PayPal Payout API failure."
        
        db.session.commit()
        logging.error(f"PayPal Payout API call failed for user {user_id}, TX_ID {withdrawal_tx.id}. Error: {payout_response.get('error')}")
        return jsonify({'error': 'PayPal Payout failed', 'details': payout_response.get('error')}), 500
