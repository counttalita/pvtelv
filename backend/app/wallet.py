from .db import db
from datetime import datetime
from sqlalchemy import Numeric, ForeignKey
from sqlalchemy.types import JSON # Added for LinkedAccount.account_details
from .models import User # For ForeignKey('user.id') reference, assuming 'user' is the table name for User model
# from enum import Enum as PyEnum # If using Python enums for account_type in LinkedAccount

# Optional: Define an Enum for account_type if desired for stricter type control
# class AccountTypeEnum(PyEnum):
#     BANK = "bank"
#     PAYPAL = "paypal"

class Wallet(db.Model):
    __tablename__ = 'wallet' # Explicitly define table name

    id = db.Column(db.Integer, primary_key=True)
    # Assuming the User model's table is named 'user'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    # Using Numeric for currency. Precision and scale (10 total digits, 2 after decimal point)
    balance = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional: Define relationship to User (if User model also defines a backref)
    # user = db.relationship('User', backref=db.backref('wallet', uselist=False))
    # Optional: Define relationship to transactions
    # transactions = db.relationship('Transaction', backref='wallet_transactions', lazy='dynamic', foreign_keys='Transaction.wallet_id')


    def __repr__(self):
        return f'<Wallet {self.user_id} - Balance: {self.balance}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'balance': str(self.balance), # Convert Decimal to string for JSON
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Transaction(db.Model):
    __tablename__ = 'transaction' # Explicitly define table name

    id = db.Column(db.Integer, primary_key=True)
    # ForeignKey references 'wallet.id' which is the tablename of Wallet model
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    # Type: e.g., 'deposit', 'withdrawal', 'fee', 'payout', 'refund'
    type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    # Currency: ISO currency code, e.g., 'ZAR', 'USD'
    currency = db.Column(db.String(3), nullable=False, default='ZAR')
    # Status: e.g., 'pending', 'completed', 'failed', 'cancelled', 'reversed'
    status = db.Column(db.String(50), nullable=False, default='pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255), nullable=True)
    external_transaction_id = db.Column(db.String(100), nullable=True, unique=True, index=True) # For PayPal TXN ID, etc.

    # Optional: Define relationship to Wallet
    # wallet = db.relationship('Wallet', backref=db.backref('transactions', lazy='dynamic', foreign_keys='Transaction.wallet_id'))


    def __repr__(self):
        return f'<Transaction {self.id} - Type: {self.type} Amount: {self.amount} {self.currency} Status: {self.status}>'

    def to_dict(self):
        return {
            'id': self.id,
            'wallet_id': self.wallet_id,
            'type': self.type,
            'amount': str(self.amount), # Convert Decimal to string for JSON
            'currency': self.currency,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'description': self.description,
            'external_transaction_id': self.external_transaction_id
        }

class LinkedAccount(db.Model):
    __tablename__ = 'linked_account' # Explicitly set table name

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Using db.String for account_type. If using Enum:
    # account_type = db.Column(db.Enum(AccountTypeEnum), nullable=False) 
    account_type = db.Column(db.String(50), nullable=False) # e.g., 'bank', 'paypal'
    
    account_details = db.Column(JSON, nullable=False) # Store bank details or PayPal email/ID
    friendly_name = db.Column(db.String(100), nullable=True) # e.g., "My Savings", "Primary PayPal"
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Optional: Define relationship to User
    # user = db.relationship('User', backref=db.backref('linked_accounts', lazy='dynamic'))

    def __repr__(self):
        return f'<LinkedAccount {self.id} - User: {self.user_id} Type: {self.account_type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_type': self.account_type,
            'account_details': self.account_details, # Assumes account_details is already JSON serializable
            'friendly_name': self.friendly_name,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
