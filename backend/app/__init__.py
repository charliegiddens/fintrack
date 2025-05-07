import os
from flask import Flask, jsonify
from flask_cors import CORS
import click
from .auth_utils import AuthError

# import extensions
from .extensions import db, cache
from .config import Config

# import blueprints
from routes.api_routes import api_bp
from routes.expense_routes import expense_bp

# application factory func
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # initialise extensions
    db.init_app(app)
    cache.init_app(app) 

    # CORS
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    app.config['FRONTEND_ORIGIN']
                    # add prod frontend env later
                ],
                "supports_credentials": True
            }
        }
    )


    # blueprint registration
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(expense_bp, url_prefix='/api/expenses')

    # Register global error handlers
    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify(error=404, text=str(e)), 404
        
    @app.route("/health")
    def health_check():
        return jsonify(status="healthy", cache_type=app.config.get("CACHE_TYPE"))

    # flask cli commands
    @app.cli.command("init-db")
    def init_db_command():
        """Clear existing data and create new tables."""
        from models import User, Expense # Import models needed for database initialisation

        with app.app_context():
            print("Initializing the database...")
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