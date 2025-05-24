import re
from app.db import db
from app.wallet import LinkedAccount # Assuming app.wallet is the correct path to models
from app.models import User # Assuming app.models is the correct path to User model
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Module constant for maximum linked accounts
MAX_LINKED_ACCOUNTS = 2

# --- Helper Functions ---

def _is_valid_email(email: str) -> bool:
    """
    Validates an email address using a simple regex.
    """
    if not email:
        return False
    # Basic regex for email validation: something@something.something
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

# --- Service Functions ---

def add_linked_account(user_id: int, account_type: str, account_details: dict, friendly_name: str = None):
    """
    Adds a new linked account for a user, subject to validation and limits.
    """
    # Check account limit
    current_accounts_count = LinkedAccount.query.filter_by(user_id=user_id).count()
    if current_accounts_count >= MAX_LINKED_ACCOUNTS:
        return {"error": "Maximum number of linked accounts reached."}

    # Validate account_type
    allowed_account_types = ['bank', 'paypal']
    if account_type not in allowed_account_types:
        return {"error": "Invalid account type. Must be 'bank' or 'paypal'."}

    # Validate account_details based on account_type
    if account_type == 'bank':
        required_bank_keys = ['bank_name', 'account_number', 'account_holder_name']
        if not all(key in account_details and account_details[key] for key in required_bank_keys):
            return {"error": "Missing required bank details (bank_name, account_number, account_holder_name)."}
    elif account_type == 'paypal':
        paypal_email = account_details.get('paypal_email')
        if not paypal_email:
            return {"error": "Missing paypal_email for PayPal account."}
        if not _is_valid_email(paypal_email):
            return {"error": "Invalid PayPal email format."}
        # Optional: Check for duplicate PayPal email for the same user if needed
        # existing_paypal = LinkedAccount.query.filter_by(user_id=user_id, account_type='paypal').first()
        # if existing_paypal and existing_paypal.account_details.get('paypal_email') == paypal_email:
        #     return {"error": "This PayPal account is already linked."}


    new_account = LinkedAccount(
        user_id=user_id,
        account_type=account_type,
        account_details=account_details, # Stored as JSON
        friendly_name=friendly_name,
        is_verified=False # Defaults to False, verification is a separate process
    )

    try:
        db.session.add(new_account)
        db.session.commit()
        return new_account # Return the ORM object on success
    except IntegrityError: # e.g., ForeignKey constraint user_id violation (though less likely if user_id is from auth)
        db.session.rollback()
        return {"error": "Database integrity error. Ensure user exists."}
    except SQLAlchemyError as e: # Catch broader SQLAlchemy errors
        db.session.rollback()
        # In a real app, log e
        print(f"SQLAlchemyError adding linked account: {e}")
        return {"error": "Could not add linked account due to a database error."}
    except Exception as e:
        db.session.rollback()
        # In a real app, log e
        print(f"Generic exception adding linked account: {e}")
        return {"error": "An unexpected error occurred while adding the linked account."}


def get_linked_accounts_for_user(user_id: int):
    """
    Retrieves all linked accounts for a given user.
    """
    try:
        return LinkedAccount.query.filter_by(user_id=user_id).all()
    except Exception as e:
        # Log e
        print(f"Exception getting linked accounts for user {user_id}: {e}")
        return [] # Return empty list on error, or raise


def get_linked_account_by_id(account_id: int, user_id: int):
    """
    Retrieves a specific linked account by its ID, ensuring it belongs to the user.
    """
    try:
        return LinkedAccount.query.filter_by(id=account_id, user_id=user_id).first()
    except Exception as e:
        # Log e
        print(f"Exception getting linked account by ID {account_id} for user {user_id}: {e}")
        return None # Return None on error, or raise


def remove_linked_account(account_id: int, user_id: int):
    """
    Removes a linked account if it exists and belongs to the user.
    """
    account_to_remove = get_linked_account_by_id(account_id, user_id)

    if not account_to_remove:
        return {"error": "Account not found or access denied."}

    try:
        db.session.delete(account_to_remove)
        db.session.commit()
        return {"success": True}
    except SQLAlchemyError as e: # Catch broader SQLAlchemy errors
        db.session.rollback()
        # Log e
        print(f"SQLAlchemyError removing linked account {account_id}: {e}")
        return {"error": "Could not remove linked account due to a database error."}
    except Exception as e:
        db.session.rollback()
        # Log e
        print(f"Generic exception removing linked account {account_id}: {e}")
        return {"error": "An unexpected error occurred while removing the linked account."}
```
