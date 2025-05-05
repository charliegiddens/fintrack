import os
from flask import current_app
from config import Config, TestingConfig

def test_development_config(app): # Use the 'app' fixture from conftest
    """Check if default config is loaded correctly (might be TestingConfig here)."""
    # Note: The app fixture always uses TestingConfig
    assert current_app.config['TESTING'] is True
    assert current_app.config['SQLALCHEMY_DATABASE_URI'] == "sqlite:///:memory:"
    assert current_app.config['SECRET_KEY'] == 'test_secretkey'
