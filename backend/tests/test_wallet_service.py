import pytest
from decimal import Decimal
from datetime import datetime

from app import create_app
from app.db import db
from app.models import User
from app.profile import create_profile # For testing integration
from app.wallet import Wallet, Transaction
from services.wallet_service import create_user_wallet, create_transaction

@pytest.fixture
def client():
    """
    Provides a Flask test client and sets up a clean database for each test.
    """
    app = create_app()
    app.config['TESTING'] = True
    # SERVER_NAME might be needed if url_for is used with _external=True in services, though not expected here.
    # app.config['SERVER_NAME'] = 'localhost.test' 
    with app.app_context():
        db.drop_all()
        db.create_all()
    with app.test_client() as client:
        # Yielding client also provides app_context for service calls if needed within tests directly
        yield client 

@pytest.fixture
def test_user(client):
    """
    Creates a basic user directly in the database for test setup.
    Relies on the client fixture to provide app_context.
    """
    user = User(phone='+15550001111', email='wallet.user@example.com')
    db.session.add(user)
    db.session.commit()
    return user

# --- Tests for create_user_wallet ---

def test_wallet_creation_on_profile_creation(client, test_user):
    """
    Tests that a wallet is automatically created when a user profile is created.
    """
    # Ensure app_context is active for create_profile which might use db.session
    with client.application.app_context():
        # create_profile itself commits the profile and triggers wallet creation
        profile = create_profile(user_id=test_user.id, display_name="Test Wallet User")
        assert profile is not None

        wallet = Wallet.query.filter_by(user_id=test_user.id).first()
        assert wallet is not None
        assert wallet.user_id == test_user.id
        assert wallet.balance == Decimal('0.00')

def test_create_user_wallet_idempotency(client, test_user):
    """
    Tests that calling create_user_wallet multiple times for the same user
    does not create multiple wallets and returns the existing wallet.
    """
    with client.application.app_context():
        wallet1 = create_user_wallet(user_id=test_user.id)
        assert wallet1 is not None
        
        wallet2 = create_user_wallet(user_id=test_user.id)
        assert wallet2 is not None
        
        assert wallet1.id == wallet2.id # Should be the same wallet object or at least same ID

        wallets_count = Wallet.query.filter_by(user_id=test_user.id).count()
        assert wallets_count == 1

def test_wallet_attributes_on_creation(client, test_user):
    """
    Tests the attributes of a newly created wallet.
    """
    with client.application.app_context():
        wallet = create_user_wallet(user_id=test_user.id)
        assert wallet is not None
        
        db_wallet = Wallet.query.filter_by(user_id=test_user.id).first()
        assert db_wallet is not None
        assert db_wallet.user_id == test_user.id
        assert db_wallet.balance == Decimal('0.00')
        assert isinstance(db_wallet.created_at, datetime)
        assert isinstance(db_wallet.updated_at, datetime)
        # created_at and updated_at should be very close for a new wallet
        assert (db_wallet.updated_at - db_wallet.created_at).total_seconds() < 5 

# --- Tests for create_transaction ---

def test_create_valid_transaction(client, test_user):
    """
    Tests creation of a transaction with all valid data.
    """
    with client.application.app_context():
        wallet = create_user_wallet(user_id=test_user.id)
        assert wallet is not None

        txn_data = {
            'wallet_id': wallet.id,
            'type': 'deposit',
            'amount': Decimal('100.50'),
            'currency': 'ZAR',
            'status': 'completed', # Assuming service allows setting status directly
            'description': 'Test deposit for services',
            'external_transaction_id': 'test_txn_wallet_001'
        }
        
        transaction = create_transaction(**txn_data)
        assert transaction is not None
        assert transaction.id is not None # Should have an ID after commit

        db_transaction = Transaction.query.get(transaction.id)
        assert db_transaction is not None
        assert db_transaction.wallet_id == wallet.id
        assert db_transaction.type == txn_data['type']
        assert db_transaction.amount == txn_data['amount']
        assert db_transaction.currency == txn_data['currency'].upper() # Service might uppercase it
        assert db_transaction.status == txn_data['status']
        assert db_transaction.description == txn_data['description']
        assert db_transaction.external_transaction_id == txn_data['external_transaction_id']
        assert isinstance(db_transaction.timestamp, datetime)

def test_create_transaction_minimal_data(client, test_user):
    """
    Tests creation of a transaction with only required fields.
    """
    with client.application.app_context():
        wallet = create_user_wallet(user_id=test_user.id)
        assert wallet is not None

        txn_data = {
            'wallet_id': wallet.id,
            'type': 'withdrawal',
            'amount': Decimal('25.00'),
            'currency': 'usd', # Test lowercase currency input
            # status defaults to 'pending' in model, service might override or use it
        }
        
        # If service sets a default status, we test that. Otherwise, model's default.
        # The `create_transaction` service function has `status: str = 'pending'`
        expected_status = 'pending'

        transaction = create_transaction(
            wallet_id=txn_data['wallet_id'],
            type=txn_data['type'],
            amount=txn_data['amount'],
            currency=txn_data['currency']
            # status is defaulted by the service function
        )
        assert transaction is not None
        assert transaction.id is not None

        db_transaction = Transaction.query.get(transaction.id)
        assert db_transaction is not None
        assert db_transaction.wallet_id == wallet.id
        assert db_transaction.type == txn_data['type']
        assert db_transaction.amount == txn_data['amount']
        assert db_transaction.currency == txn_data['currency'].upper() # Service standardizes
        assert db_transaction.status == expected_status # Default from service
        assert db_transaction.description is None
        assert db_transaction.external_transaction_id is None
        assert isinstance(db_transaction.timestamp, datetime)

def test_transaction_belongs_to_wallet(client, test_user):
    """
    Tests that a created transaction correctly references its parent wallet.
    """
    with client.application.app_context():
        wallet = create_user_wallet(user_id=test_user.id)
        assert wallet is not None

        transaction = create_transaction(
            wallet_id=wallet.id,
            type='fee',
            amount=Decimal('1.20'),
            currency='EUR'
        )
        assert transaction is not None
        
        db_transaction = Transaction.query.get(transaction.id)
        assert db_transaction is not None
        assert db_transaction.wallet_id == wallet.id

        # Optional: If relationships were defined and working:
        # fetched_wallet = Wallet.query.get(wallet.id)
        # assert transaction in fetched_wallet.transactions (if relationship is eager or queried)
        # Or:
        # assert db_transaction.wallet == fetched_wallet (if relationship is defined on Transaction)
        
def test_create_transaction_handles_string_amount(client, test_user):
    """
    Tests that create_transaction correctly converts string amounts to Decimal.
    """
    with client.application.app_context():
        wallet = create_user_wallet(user_id=test_user.id)
        assert wallet is not None

        transaction = create_transaction(
            wallet_id=wallet.id,
            type='deposit',
            amount='150.75', # Amount as string
            currency='GBP'
        )
        assert transaction is not None
        assert transaction.amount == Decimal('150.75')

        db_transaction = Transaction.query.get(transaction.id)
        assert db_transaction.amount == Decimal('150.75')

def test_create_transaction_invalid_amount_type(client, test_user):
    """
    Tests that create_transaction returns None or raises error for invalid amount types
    that cannot be converted to Decimal by the service function.
    """
    with client.application.app_context():
        wallet = create_user_wallet(user_id=test_user.id)
        assert wallet is not None

        # The service function currently prints an error and returns None.
        transaction = create_transaction(
            wallet_id=wallet.id,
            type='deposit',
            amount={'invalid': 'type'}, # Invalid amount type
            currency='USD'
        )
        assert transaction is None
        # In a real app, this might raise a specific ValueError.
        # For now, we test the current behavior (returns None).
```
