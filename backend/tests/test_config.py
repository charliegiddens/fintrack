import os
from flask import current_app
from config import Config, TestingConfig

def test_development_config(app):
    """Check if TestingConfig is loaded correctly."""

    assert current_app.config['TESTING'] is True
    assert current_app.config['SQLALCHEMY_DATABASE_URI'] == "sqlite:///:memory:"
    assert current_app.config['SECRET_KEY'] == 'test_secretkey'
