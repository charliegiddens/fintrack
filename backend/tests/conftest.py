import pytest
from app import create_app
from app.config import TestingConfig
from app.extensions import db as _db

# --- Core Fixtures ---

@pytest.fixture(scope='session')
def app():
    """
    Session-wide test Flask application configured for testing.
    Creates the app instance once per test session.
    """
    _app = create_app(config_class=TestingConfig)

    # Establish an application context before running tests
    # Necessary for things like url_for, accessing current_app, etc.
    ctx = _app.app_context()
    ctx.push()
    print("\n--- Pushed Test Application Context (Session Scope) ---")

    yield _app # Provide the _app instance to the tests

    ctx.pop() # Clean up context
    print("\n--- Popped Test Application Context (Session Scope) ---")

@pytest.fixture(scope='function')
def client(app):
    """
    Provides a Flask test client for making requests.
    Runs once per test function.
    """
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """
    Provides a Flask test CLI runner for invoking commands.
    Runs once per test function.
    """
    return app.test_cli_runner()

# --- Database Fixtures ---

@pytest.fixture(scope='session')
def db(app):
    """
    Session-wide test database management.
    Creates tables once per session and drops them afterwards.
    """
    _db.app = app # Associate the db extension instance with the test app
    with app.app_context():
        print("\n--- Creating Test Database Tables (Session Scope) ---")
        _db.create_all()

    yield _db # Provide the db instance to tests using it

    # Explicitly close connections after tests are done
    _db.engine.dispose()

    with app.app_context():
        print("\n--- Dropping Test Database Tables (Session Scope) ---")
        _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    """
    Ensures test isolation by running each test within a database transaction
    that is rolled back afterwards. Makes the app's db.session use this transaction.
    """
    # Obtain a connection from the engine managed by the db fixture
    connection = db.engine.connect()
    # Begin a transaction
    transaction = connection.begin()

    # Bind the application's scoped session to this transaction/connection.
    # All db.session operations within the test will now use this transaction.
    db.session.configure(bind=connection)

    yield db.session # Yield the application's db.session proxy

    # Teardown: Rollback the transaction and close the connection
    # print("\n--- Rolling Back Test Transaction (Function Scope) ---") # Debug
    db.session.remove() # Crucial: remove the scoped session context
    transaction.rollback()
    connection.close()
    # Reset the session binding after the test (optional but cleaner)
    db.session.configure(bind=db.engine)
