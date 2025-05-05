# app.py
import os
from flask import Flask

# --- Import Extensions and Config ---
from extensions import db, oauth
from config import Config
# --- Import Blueprints from the 'routes' package ---
from routes.main import main_bp # Import main blueprint
from routes.auth import auth_bp # Import auth blueprint

# --- Application Factory Function ---
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions
    db.init_app(app)
    oauth.init_app(app)

    # Configure Auth0 Provider (needs initialized oauth)
    oauth.register(
        "auth0",
        client_id=app.config['AUTH0_CLIENT_ID'],
        client_secret=app.config['AUTH0_CLIENT_SECRET'],
        client_kwargs={"scope": "openid profile email",},
        server_metadata_url=f'https://{app.config["AUTH0_DOMAIN"]}/.well-known/openid-configuration'
    )

    # --- Register Blueprints ---
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    # Register other blueprints here
    # app.register_blueprint(expenses_bp, url_prefix='/expenses') # Example with prefix

    # --- Define CLI Commands ---
    @app.cli.command("init-db")
    def init_db_command():
        """Clear existing data and create new tables."""
        from models import User, Expense # Import models needed

        with app.app_context():
            print("Initializing the database...")
            # db.drop_all() # Optional for dev reset
            db.create_all()
            print("Database initialized!")

    return app

# --- Run the App ---
if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=5000, debug=True)