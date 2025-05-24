import os # Added import
from dotenv import load_dotenv # Added for .env loading
from app import create_app

load_dotenv() # Load environment variables from .env file

app = create_app()

# Load PayPal configuration from environment variables
app.config['PAYPAL_MODE'] = os.environ.get('PAYPAL_MODE', 'sandbox')
app.config['PAYPAL_CLIENT_ID'] = os.environ.get('PAYPAL_CLIENT_ID')
app.config['PAYPAL_CLIENT_SECRET'] = os.environ.get('PAYPAL_CLIENT_SECRET')
app.config['PAYPAL_WEBHOOK_ID'] = os.environ.get('PAYPAL_WEBHOOK_ID')

# Initialize PayPal SDK
from services.paypal_service import initialize_paypal
if not initialize_paypal(app.config):
    # Potentially raise an error or log critical failure if PayPal is essential
    # For now, just print a warning. In a real app, this might be a critical failure.
    print("WARNING: PayPal SDK failed to initialize. Check configuration and logs.")

# Register Blueprints
from app.routes_wallet import wallet_bp
app.register_blueprint(wallet_bp, url_prefix='/api/wallet')
# Add other blueprints here as the app grows


if __name__ == '__main__':
    app.run(debug=True)
