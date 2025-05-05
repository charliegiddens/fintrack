# app.py
import os
from flask import Flask
# Removed route-specific imports like session, redirect, url_for, render_template etc.

# --- Import Extensions, Config, and Blueprints ---
from extensions import db, oauth # Import db and oauth instances
from config import Config
from routes import main_bp # Import the Blueprint from routes.py

# --- Application Factory Function ---
def create_app(config_class=Config):
    app = Flask(__name__)
    # --- Load Configuration ---
    app.config.from_object(config_class)

    # --- Initialize Extensions with the app instance ---
    db.init_app(app)
    oauth.init_app(app) # Initialize OAuth with the app

    # --- Configure Auth0 OAuth Provider (needs initialized oauth) ---
    # This registers the 'auth0' client with the oauth object initialized above
    oauth.register(
        "auth0",
        client_id=app.config['AUTH0_CLIENT_ID'], # Use app.config
        client_secret=app.config['AUTH0_CLIENT_SECRET'], # Use app.config
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=f'https://{app.config["AUTH0_DOMAIN"]}/.well-known/openid-configuration'
    )

    # --- Register Blueprints ---
    app.register_blueprint(main_bp)
    # If you had other blueprints (e.g., for API), register them here:
    # from routes_api import api_bp
    # app.register_blueprint(api_bp, url_prefix='/api')

    # --- Define CLI Commands ---
    @app.cli.command("init-db")
    def init_db_command():
        """Clear existing data and create new tables."""
        # Update model imports
        from models import User, Expense # Changed Transaction to Expense

        with app.app_context():
            print("Initializing the database...")
            # IMPORTANT: If the 'transactions' table exists from before,
            # db.create_all() will NOT remove it. It will only create 'expenses'.
            # For development, you might temporarily add db.drop_all()
            # or manually drop the old table.
            # db.drop_all() # <--- Add temporarily for clean slate if needed
            # print("Dropped existing tables.")
            db.create_all()
            print("Database initialized! Tables created/checked.")

    # Return the configured app instance
    return app

# --- Run the App (using the factory) ---
if __name__ == "__main__":
    flask_app = create_app()
    # Make sure templates can access session easily (if not already default)
    # flask_app.jinja_env.globals.update(session=session) # Usually not needed
    flask_app.run(host="0.0.0.0", port=5000, debug=True)