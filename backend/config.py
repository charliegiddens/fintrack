import os
from dotenv import load_dotenv
from urllib.parse import quote_plus, urlencode

# Load environment variables from .env file into the environment
load_dotenv()

class Config:
    """Base configuration variables."""
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False # Base config is not for testing

    # flask cli authentication key
    CLI_KEY = os.environ.get('CLI_KEY')

    # Load DB components from environment
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD_RAW = os.environ.get('DB_PASSWORD')
    DB_SERVER = os.environ.get('DB_SERVER')
    DB_PORT = os.environ.get('DB_PORT', '1433')
    DB_DATABASE = os.environ.get('DB_DATABASE')
    DB_DRIVER = os.environ.get('DB_DRIVER', 'ODBC Driver 18 for SQL Server')

    # Check all DB env variables are declared.
    if not all([DB_USER, DB_PASSWORD_RAW, DB_SERVER, DB_DATABASE, DB_DRIVER]):
        print("--- DEBUG: One or more DB env vars missing! ---")
        print(f"DB_USER: {'Set' if DB_USER else 'MISSING'}")
        print(f"DB_PASSWORD_RAW: {'Set' if DB_PASSWORD_RAW else 'MISSING'}")
        print(f"DB_SERVER: {'Set' if DB_SERVER else 'MISSING'}")
        print(f"DB_DATABASE: {'Set' if DB_DATABASE else 'MISSING'}")
        print(f"DB_DRIVER: {'Set' if DB_DRIVER else 'MISSING'}")
        raise ValueError("Missing one or more core database environment variables")

    # Construct DB URI only if not testing (and if all vars are present)
    SQLALCHEMY_DATABASE_URI = None
    if DB_USER and DB_PASSWORD_RAW and DB_SERVER and DB_DATABASE and DB_DRIVER:
        DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD_RAW)
        query_params = {'driver': DB_DRIVER, 'Encrypt': 'yes', 'TrustServerCertificate': 'no'}
        query_string = urlencode(query_params)
        SQLALCHEMY_DATABASE_URI = (
            f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_SERVER}:{DB_PORT}/"
            f"{DB_DATABASE}?{query_string}"
        )
    elif not TESTING:
        print("Warning: Standard DB environment variables not fully set.")

    # --- Auth0 Config ---
    AUTH0_CLIENT_ID = os.environ.get('AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.environ.get('AUTH0_CLIENT_SECRET')
    AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN')
    AUTH0_API_AUDIENCE = os.environ.get('AUTH0_API_AUDIENCE')

    # --- Redis Config ---
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'RedisCache')
    CACHE_REDIS_HOST = os.environ.get('CACHE_REDIS_HOST')
    CACHE_REDIS_PORT = int(os.environ.get('CACHE_REDIS_PORT'))
    CACHE_REDIS_PASSWORD = os.environ.get('CACHE_REDIS_PASSWORD')
    CACHE_REDIS_DB = int(os.environ.get('CACHE_REDIS_DB', 0))
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    CACHE_REDIS_URI = None
    if CACHE_REDIS_HOST and CACHE_REDIS_PORT and CACHE_REDIS_PASSWORD and CACHE_REDIS_DB:
        CACHE_REDIS_PASSWORD_ENCODED = quote_plus(CACHE_REDIS_PASSWORD)
        CACHE_REDIS_URI = (
            f"rediss://:{CACHE_REDIS_PASSWORD_ENCODED}@{CACHE_REDIS_HOST}:{CACHE_REDIS_PORT}/{CACHE_REDIS_DB}"
        )


    if not TESTING and not all([AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN, AUTH0_API_AUDIENCE]):
        print("Warning: Auth0 environment variables not fully set.")

class TestingConfig(Config):
    """Testing-specific configuration."""
    TESTING = True
    # in-memory SQLite database for tests
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # Define server name for testing exteral url gen
    SERVER_NAME = "localhost"

    # Caching for tests
    CACHE_TYPE = 'SimpleCache' # Use simplecache so tests dont need our external redis instance

    SECRET_KEY = 'test_secretkey' # Simple key adequate for tests
    # Dummy Auth0 values for testing config (mocks will bypass actual use)
    AUTH0_DOMAIN = 'testing.auth0.com'
    AUTH0_CLIENT_ID = 'test_client_id'
    AUTH0_CLIENT_SECRET = 'test_client_secret'
