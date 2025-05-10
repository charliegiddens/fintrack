from flask import Flask, jsonify
from flask_migrate import Migrate
from .auth_utils import AuthError
import os

# import extensions
from .extensions import db, cache
from .config import DevelopmentConfig, StagingConfig, ProductionConfig

# import blueprints
from routes.api_routes import api_bp
from routes.expense_routes import expense_bp

# application factory func
def create_app(config_class=None):
    app = Flask(__name__)

    # Select appropriate config per flask environment
    match os.getenv("FLASK_ENV"):
        case "development":
            app.config.from_object(DevelopmentConfig)
            app.debug = True
        case "staging":
            app.config.from_object(StagingConfig)
        case "production":
            app.config.from_object(ProductionConfig)
        case _:
            raise RuntimeError("FLASK_ENV must be set to 'development', 'staging', or 'production'") 
        

    # initialise extensions
    db.init_app(app)
    cache.init_app(app) 

    # Set up Flask-Migrate
    Migrate(app, db)

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

    return app

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=5000, debug=True)