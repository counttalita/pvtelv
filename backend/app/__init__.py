from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import db
import os
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///pvtelv.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .registration import registration_bp
    from .verification import verification_bp
    from .login import login_bp
    from .routes_kyc import kyc_bp
    app.register_blueprint(registration_bp)
    app.register_blueprint(verification_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(kyc_bp)
    from .routes_profile import profile_bp
    app.register_blueprint(profile_bp)

    with app.app_context():
        db.create_all()

    return app
