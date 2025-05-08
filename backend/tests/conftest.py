import pytest
from flask import Flask
from unittest.mock import MagicMock


from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.config import TestingConfig
from app.extensions import db as _db
from routes.expense_routes import expense_bp

# Enabling FK pragma to avoid IntegrityErrors when testing models
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraint enforcement for SQLite connections."""
    if dbapi_connection.__class__.__module__ == "sqlite3":
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

@pytest.fixture(scope="function")
def app():
    _app = Flask(__name__)
    _app.config.from_object(TestingConfig)
    _app.logger = MagicMock()

    with _app.app_context():
        _db.init_app(_app)
        
        # tested route blueprints
        _app.register_blueprint(expense_bp)

    yield _app

@pytest.fixture(scope="function")
def db(app):
    """
    Function-scoped database fixture.
    Creates all tables before each test and drops them afterwards.
    """
    with app.app_context():
        _db.create_all()

        yield _db 

        with app.app_context():
            _db.session.remove()
            _db.drop_all()

@pytest.fixture
def client(app): # Remains useful for route tests later
    return app.test_client()

# --- Auth Mocking Fixtures ---
MOCK_AUTH0_SUBJECT_ID = "auth0|testuser123"
MOCK_FINTRACK_USER_ID = 1

#

# --- Mock Fixtures for requires_auth dependencies ---
@pytest.fixture
def mock_get_token_auth_header(mocker):
    """Mocks app.auth_utils.get_token_auth_header"""
    return mocker.patch('app.auth_utils.get_token_auth_header')

@pytest.fixture
def mock_get_jwks_from_auth0_uncached(mocker):
    """Mocks app.auth_utils.get_jwks_from_auth0_uncached"""
    return mocker.patch('app.auth_utils.get_jwks_from_auth0_uncached')

@pytest.fixture
def mock_verify_decode_jwt(mocker):
    """Mocks app.auth_utils.verify_decode_jwt"""
    return mocker.patch('app.auth_utils.verify_decode_jwt')

#

@pytest.fixture
def seed_test_user(db):
    from models.user import User # Local import to avoid circular dependency issues at load time
    user = User(id=MOCK_FINTRACK_USER_ID, auth0_subject=MOCK_AUTH0_SUBJECT_ID, email="test@example.com")
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def app_context(app):
    with app.app_context():
        yield

@pytest.fixture
def request_context(app):
    with app.test_request_context('/fake-endpoint'):
        yield

# Sample data (should ideally use values from TestingConfig if they match)
SAMPLE_JWKS = {
    "keys": [{
        "alg": TestingConfig.ALGORITHMS, 
        "kty": "RSA", 
        "use": "sig", 
        "n": "n4EPtA...", 
        "e": "AQAB", 
        "kid": TestingConfig.KID
    }]
}
# Using TestingConfig for consistency
SAMPLE_PAYLOAD = {
    "iss": f"https://{TestingConfig.AUTH0_DOMAIN}/",
    "sub": "auth0|user123",
    "aud": TestingConfig.AUTH0_API_AUDIENCE,
    "exp": 9999999999, "iat": 1500000000
}
TEST_TOKEN = "fake.jwt.token"
SAMPLE_UNVERIFIED_HEADER = {"alg": "RS256", "typ": "JWT", "kid": "test_kid_123"}

@pytest.fixture
def mock_auth_utils_cache(mocker):
    """
    Mocks the 'cache' object as imported and used within 'app.auth_utils'.
    The patch target 'app.auth_utils.cache' assumes 'auth_utils.py' is in the 'app' package
    and imports cache as 'from .extensions import cache'.
    """
    mock_cache_instance = MagicMock()
    # .memoize(timeout) returns a decorator. That decorator(func) returns func.
    mock_cache_instance.memoize = MagicMock(side_effect=lambda timeout: lambda func: func)
    mock_cache_instance.delete_memoized = MagicMock()

    # Patch 'cache' where it's referenced in app.auth_utils
    mocker.patch('app.auth_utils.cache', new=mock_cache_instance)
    return mock_cache_instance

@pytest.fixture(autouse=True)
def mock_auth_for_protected_routes(
    mocker,
    mock_get_token_auth_header,
    mock_get_jwks_from_auth0_uncached,
    mock_verify_decode_jwt,
    mock_auth_utils_cache
):
    """
    Automatically mock auth and internal user lookup for all protected route tests.
    """
    mock_get_token_auth_header.return_value = "Bearer test-token"
    mock_get_jwks_from_auth0_uncached.return_value = {"keys": []}
    mock_verify_decode_jwt.return_value = {"sub": MOCK_AUTH0_SUBJECT_ID}

    mocker.patch(
        "app.api_helpers.get_internal_user_id_from_auth0_sub",
        return_value=MOCK_FINTRACK_USER_ID
    )
