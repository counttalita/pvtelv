from app.db import db
from app.wallet import Wallet, Transaction # Assuming direct import path from app root
from sqlalchemy.exc import IntegrityError
from decimal import Decimal # For handling precise monetary values

def create_user_wallet(user_id):
    """
    Creates a new wallet for a user if one doesn't already exist.
    """
    existing_wallet = Wallet.query.filter_by(user_id=user_id).first()
    if existing_wallet:
        # Optionally log that wallet already exists, but returning it is fine
        return existing_wallet

    new_wallet = Wallet(user_id=user_id, balance=Decimal('0.00'))
    try:
        db.session.add(new_wallet)
        db.session.commit()
        return new_wallet
    except IntegrityError as e:
        db.session.rollback()
        # This might happen if, due to a race condition, a wallet was created
        # between the check and the commit. Or if user_id is not valid.
        # Log the error
        print(f"IntegrityError creating wallet for user_id {user_id}: {e}") # Replace with actual logging
        # Try to fetch again in case of race condition
        return Wallet.query.filter_by(user_id=user_id).first()
    except Exception as e:
        db.session.rollback()
        # Log other potential errors
        print(f"Exception creating wallet for user_id {user_id}: {e}") # Replace with actual logging
        return None


def create_transaction(wallet_id: int, type: str, amount: Decimal, 
                       currency: str, status: str = 'pending', 
                       description: str = None, external_transaction_id: str = None):
    """
    Creates a new transaction for a given wallet.
    Amount should be a Decimal.
    """
    if not isinstance(amount, Decimal):
        try:
            amount = Decimal(str(amount)) # Convert if string or float, ensure precision
        except Exception as e:
            print(f"Invalid amount type for transaction: {amount}, Error: {e}") # Replace with actual logging
            return None # Or raise ValueError

    new_transaction = Transaction(
        wallet_id=wallet_id,
        type=type,
        amount=amount,
        currency=currency.upper(), # Standardize currency code
        status=status,
        description=description,
        external_transaction_id=external_transaction_id
    )
    try:
        db.session.add(new_transaction)
        db.session.commit()
        return new_transaction
    except Exception as e:
        db.session.rollback()
        # Log the error
        print(f"Exception creating transaction for wallet_id {wallet_id}: {e}") # Replace with actual logging
        return None
