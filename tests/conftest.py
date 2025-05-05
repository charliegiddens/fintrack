import pytest
from app import create_app # Your app factory
from config import TestingConfig # Your testing config class
from extensions import db as _db # Your database extension instance

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
    _db.session.close_all()
    # _db.engine.dispose() # May be needed in some scenarios

    with app.app_context():
        print("\n--- Dropping Test Database Tables (Session Scope) ---")
        _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    """
    Manages DB transactions for each test function.
    Starts a transaction, yields the session, and rolls back afterwards.
    Ensures test isolation.
    """
    connection = db.engine.connect()
    transaction = connection.begin()

    # Use the connection for the session object provided to the test
    options = dict(bind=connection, binds={})
    sess = db.create_scoped_session(options=options)

    # Overwrite the default session object with this transaction-bound session
    db.session = sess
    # print("\n--- Started DB Transaction (Function Scope) ---") # Debug

    yield sess # This is the session object tests should use for DB operations

    # Teardown: rollback transaction and close connection
    sess.remove()
    transaction.rollback()
    connection.close()
    # print("\n--- Rolled Back DB Transaction (Function Scope) ---") # Debug
