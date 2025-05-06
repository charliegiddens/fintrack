import os
from flask import Flask
import click

# import extensions
from extensions import db, oauth, cache
from config import Config

# import route blueprints
from routes.main import main_bp # main blueprint
from routes.auth import auth_bp # auth blueprint

# application factory func
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # initialise extensions
    db.init_app(app)
    oauth.init_app(app)
    cache.init_app(app) 

    # Auth0 config
    oauth.register(
        "auth0",
        client_id=app.config['AUTH0_CLIENT_ID'],
        client_secret=app.config['AUTH0_CLIENT_SECRET'],
        client_kwargs={"scope": "openid profile email",},
        server_metadata_url=f'https://{app.config["AUTH0_DOMAIN"]}/.well-known/openid-configuration'
    )

    # blueprint registration
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # flask cli commands
    @app.cli.command("init-db")
    def init_db_command():
        """Clear existing data and create new tables."""
        from models import User, Expense # Import models needed for database initialisation

        with app.app_context():
            print("Initializing the database...")
            # db.drop_all() # Optional for dev reset
            db.create_all()
            print("Database initialized!")
    
    @app.cli.command("drop-db")
    def drop_db_command():
        """Drop all tables."""
        if click.confirm("This command will drop the WHOLE database. Are you absolutely sure you want to do this?"):
            if click.prompt('Input the CLI authentication key') == app.config['CLI_KEY']:
                with app.app_context():
                    print("Dropping the database...")
                    db.drop_all()
                    print("Database dropped!")

    return app

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=5000, debug=True)