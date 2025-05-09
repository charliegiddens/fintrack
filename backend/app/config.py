import os
from dotenv import load_dotenv
from urllib.parse import quote_plus, urlencode

load_dotenv()

class Config:
    """Base configuration variables."""
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False

    # CORS
    FRONTEND_ORIGIN = os.environ.get('FRONTEND_ORIGIN')

    # Load DB components from environment
    DB_PROTOCOL = os.environ.get('STAGING_DB_PROTOCOL')
    DB_USER = os.environ.get('STAGING_DB_USER')
    DB_PASSWORD_RAW = os.environ.get('STAGING_DB_PASSWORD')
    DB_SERVER = os.environ.get('STAGING_DB_SERVER')
    DB_PORT = os.environ.get('STAGING_DB_PORT')
    DB_DATABASE = os.environ.get('STAGING_DB_DATABASE')
    DB_DRIVER = os.environ.get('STAGING_DB_DRIVER')

    # Check all DB env variables are declared.
    if not all([DB_PROTOCOL, DB_USER, DB_PASSWORD_RAW, DB_SERVER, DB_DATABASE, DB_DRIVER]):
        print("--- DEBUG: One or more DB env vars missing! ---")
        print(f"DB_PROTOCOL: {'Set' if DB_PROTOCOL else 'MISSING'}")
        print(f"DB_USER: {'Set' if DB_USER else 'MISSING'}")
        print(f"DB_PASSWORD_RAW: {'Set' if DB_PASSWORD_RAW else 'MISSING'}")
        print(f"DB_SERVER: {'Set' if DB_SERVER else 'MISSING'}")
        print(f"DB_DATABASE: {'Set' if DB_DATABASE else 'MISSING'}")
        print(f"DB_DRIVER: {'Set' if DB_DRIVER else 'MISSING'}")
        raise ValueError("Missing one or more core database environment variables")

    # Construct DB URI only if not testing (and if all vars are present)
    SQLALCHEMY_DATABASE_URI = None
    if DB_PROTOCOL and DB_USER and DB_PASSWORD_RAW and DB_SERVER and DB_DATABASE and DB_DRIVER:
        DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD_RAW)
        query_params = {'driver': DB_DRIVER, 'Encrypt': 'yes', 'TrustServerCertificate': 'no'}
        query_string = urlencode(query_params)
        SQLALCHEMY_DATABASE_URI = (
            f"{DB_PROTOCOL}://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_SERVER}:{DB_PORT}/"
            f"{DB_DATABASE}?{query_string}"
        )
    elif not TESTING:
        print("Warning: Standard DB environment variables not fully set.")

    # --- Auth0 Config ---
    AUTH0_CLIENT_ID = os.environ.get('STAGING_AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.environ.get('STAGING_AUTH0_CLIENT_SECRET')
    AUTH0_DOMAIN = os.environ.get('STAGING_AUTH0_DOMAIN')
    AUTH0_API_AUDIENCE = os.environ.get('STAGING_AUTH0_API_AUDIENCE')

    # --- Redis Config ---
    CACHE_TYPE = os.getenv("STAGING_CACHE_TYPE")
    CACHE_REDIS_SSL = os.getenv("STAGING_CACHE_REDIS_SSL")
    CACHE_PROTOCOL = os.getenv("STAGING_CACHE_PROTOCOL")
    CACHE_DEFAULT_TIMEOUT = os.getenv("STAGING_CACHE_DEFAULT_TIMEOUT")
    CACHE_ACCESS_KEY = os.getenv("STAGING_CACHE_ACCESS_KEY")
    CACHE_SERVER = os.getenv("STAGING_CACHE_SERVER")
    CACHE_PORT = os.getenv("STAGING_CACHE_PORT")
    ALGORITHMS = os.getenv("STAGING_CACHE_ALGORITHMS")

    if not all([CACHE_TYPE, CACHE_REDIS_SSL, CACHE_PROTOCOL, CACHE_DEFAULT_TIMEOUT, CACHE_ACCESS_KEY, CACHE_SERVER, CACHE_PORT, ALGORITHMS]):
        print("--- DEBUG: One or more DB env vars missing! ---")
        print(f"CACHE_TYPE: {'Set' if CACHE_TYPE else 'MISSING'}")
        print(f"CACHE_REDIS_SSL: {'Set' if CACHE_REDIS_SSL else 'MISSING'}")
        print(f"CACHE_PROTOCOL: {'Set' if CACHE_PROTOCOL else 'MISSING'}")
        print(f"CACHE_DEFAULT_TIMEOUT: {'Set' if CACHE_DEFAULT_TIMEOUT else 'MISSING'}")
        print(f"CACHE_ACCESS_KEY: {'Set' if CACHE_ACCESS_KEY else 'MISSING'}")
        print(f"CACHE_SERVER: {'Set' if CACHE_SERVER else 'MISSING'}")
        print(f"CACHE_PORT: {'Set' if CACHE_PORT else 'MISSING'}")
        print(f"ALGORITHMS: {'Set' if ALGORITHMS else 'MISSING'}")
        raise ValueError("Missing one or more core Redis environment variables")

    CACHE_REDIS_URL = None
    if CACHE_PROTOCOL and CACHE_ACCESS_KEY and CACHE_SERVER and CACHE_PORT:
        DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD_RAW)
        query_params = {'driver': DB_DRIVER, 'Encrypt': 'yes', 'TrustServerCertificate': 'no'}
        query_string = urlencode(query_params)
        CACHE_REDIS_URL = (
            f"{CACHE_PROTOCOL}://:{CACHE_ACCESS_KEY}@{CACHE_SERVER}:{CACHE_PORT}/0"
        )

    if not TESTING and not all([AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN, AUTH0_API_AUDIENCE]):
        print("Warning: Auth0 environment variables not fully set.")

class DevelopmentConfig():
    """Development configuration variables."""
    SECRET_KEY = os.environ.get('DEV_APP_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS
    FRONTEND_ORIGIN = os.environ.get('DEV_FRONTEND_ORIGIN')

    # Database URI for local development (SQLite in-memory)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DB_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis configuration
    CACHE_TYPE = os.environ.get("DEV_CACHE_TYPE")
    CACHE_DEFAULT_TIMEOUT = 300

    # Auth0 - In development, you might use a different set of credentials for testing
    AUTH0_CLIENT_ID = os.environ.get('DEV_AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.environ.get('DEV_AUTH0_CLIENT_SECRET')
    AUTH0_DOMAIN = os.environ.get('DEV_AUTH0_DOMAIN')
    AUTH0_API_AUDIENCE = os.environ.get('DEV_AUTH0_API_AUDIENCE')

class StagingConfig():
    """Staging configuration variables."""
    SECRET_KEY = os.environ.get('STAGING_APP_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False

    # CORS
    FRONTEND_ORIGIN = os.environ.get('STAGING_FRONTEND_ORIGIN')

    # Load DB components from environment
    DB_PROTOCOL = os.environ.get('STAGING_DB_PROTOCOL')
    DB_USER = os.environ.get('STAGING_DB_USER')
    DB_PASSWORD_RAW = os.environ.get('STAGING_DB_PASSWORD')
    DB_SERVER = os.environ.get('STAGING_DB_SERVER')
    DB_PORT = os.environ.get('STAGING_DB_PORT')
    DB_DATABASE = os.environ.get('STAGING_DB_DATABASE')
    DB_DRIVER = os.environ.get('STAGING_DB_DRIVER')

    # Check all DB env variables are declared.
    if not all([DB_PROTOCOL, DB_USER, DB_PASSWORD_RAW, DB_SERVER, DB_DATABASE, DB_DRIVER]):
        print("--- DEBUG: One or more DB env vars missing! ---")
        print(f"DB_PROTOCOL: {'Set' if DB_PROTOCOL else 'MISSING'}")
        print(f"DB_USER: {'Set' if DB_USER else 'MISSING'}")
        print(f"DB_PASSWORD_RAW: {'Set' if DB_PASSWORD_RAW else 'MISSING'}")
        print(f"DB_SERVER: {'Set' if DB_SERVER else 'MISSING'}")
        print(f"DB_DATABASE: {'Set' if DB_DATABASE else 'MISSING'}")
        print(f"DB_DRIVER: {'Set' if DB_DRIVER else 'MISSING'}")
        raise ValueError("Missing one or more core database environment variables")

    # Construct DB URI only if not testing (and if all vars are present)
    SQLALCHEMY_DATABASE_URI = None
    if DB_PROTOCOL and DB_USER and DB_PASSWORD_RAW and DB_SERVER and DB_DATABASE and DB_DRIVER:
        DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD_RAW)
        query_params = {'driver': DB_DRIVER, 'Encrypt': 'yes', 'TrustServerCertificate': 'no'}
        query_string = urlencode(query_params)
        SQLALCHEMY_DATABASE_URI = (
            f"{DB_PROTOCOL}://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_SERVER}:{DB_PORT}/"
            f"{DB_DATABASE}?{query_string}"
        )
    elif not TESTING:
        print("Warning: Standard DB environment variables not fully set.")

    # --- Auth0 Config ---
    AUTH0_CLIENT_ID = os.environ.get('STAGING_AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.environ.get('STAGING_AUTH0_CLIENT_SECRET')
    AUTH0_DOMAIN = os.environ.get('STAGING_AUTH0_DOMAIN')
    AUTH0_API_AUDIENCE = os.environ.get('STAGING_AUTH0_API_AUDIENCE')

    # --- Redis Config ---
    CACHE_TYPE = os.getenv("STAGING_CACHE_TYPE")
    CACHE_REDIS_SSL = os.getenv("STAGING_CACHE_REDIS_SSL")
    CACHE_PROTOCOL = os.getenv("STAGING_CACHE_PROTOCOL")
    CACHE_DEFAULT_TIMEOUT = os.getenv("STAGING_CACHE_DEFAULT_TIMEOUT")
    CACHE_ACCESS_KEY = os.getenv("STAGING_CACHE_ACCESS_KEY")
    CACHE_SERVER = os.getenv("STAGING_CACHE_SERVER")
    CACHE_PORT = os.getenv("STAGING_CACHE_PORT")
    ALGORITHMS = os.getenv("STAGING_CACHE_ALGORITHMS")

    if not all([CACHE_TYPE, CACHE_REDIS_SSL, CACHE_PROTOCOL, CACHE_DEFAULT_TIMEOUT, CACHE_ACCESS_KEY, CACHE_SERVER, CACHE_PORT, ALGORITHMS]):
        print("--- DEBUG: One or more DB env vars missing! ---")
        print(f"CACHE_TYPE: {'Set' if CACHE_TYPE else 'MISSING'}")
        print(f"CACHE_REDIS_SSL: {'Set' if CACHE_REDIS_SSL else 'MISSING'}")
        print(f"CACHE_PROTOCOL: {'Set' if CACHE_PROTOCOL else 'MISSING'}")
        print(f"CACHE_DEFAULT_TIMEOUT: {'Set' if CACHE_DEFAULT_TIMEOUT else 'MISSING'}")
        print(f"CACHE_ACCESS_KEY: {'Set' if CACHE_ACCESS_KEY else 'MISSING'}")
        print(f"CACHE_SERVER: {'Set' if CACHE_SERVER else 'MISSING'}")
        print(f"CACHE_PORT: {'Set' if CACHE_PORT else 'MISSING'}")
        print(f"ALGORITHMS: {'Set' if ALGORITHMS else 'MISSING'}")
        raise ValueError("Missing one or more core Redis environment variables")

    CACHE_REDIS_URL = None
    if CACHE_PROTOCOL and CACHE_ACCESS_KEY and CACHE_SERVER and CACHE_PORT:
        DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD_RAW)
        query_params = {'driver': DB_DRIVER, 'Encrypt': 'yes', 'TrustServerCertificate': 'no'}
        query_string = urlencode(query_params)
        CACHE_REDIS_URL = (
            f"{CACHE_PROTOCOL}://:{CACHE_ACCESS_KEY}@{CACHE_SERVER}:{CACHE_PORT}/0"
        )

    if not TESTING and not all([AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN, AUTH0_API_AUDIENCE]):
        print("Warning: Auth0 environment variables not fully set.")

class ProductionConfig():
    """Production configuration variables."""
    SECRET_KEY = os.environ.get('PROD_APP_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False

    # CORS
    FRONTEND_ORIGIN = os.environ.get('PROD_FRONTEND_ORIGIN')

    # Load DB components from environment
    DB_PROTOCOL = os.environ.get('PROD_DB_PROTOCOL')
    DB_USER = os.environ.get('PROD_DB_USER')
    DB_PASSWORD_RAW = os.environ.get('PROD_DB_PASSWORD')
    DB_SERVER = os.environ.get('PROD_DB_SERVER')
    DB_PORT = os.environ.get('PROD_DB_PORT')
    DB_DATABASE = os.environ.get('PROD_DB_DATABASE')
    DB_DRIVER = os.environ.get('PROD_DB_DRIVER')

    # Check all DB env variables are declared.
    if not all([DB_PROTOCOL, DB_USER, DB_PASSWORD_RAW, DB_SERVER, DB_DATABASE, DB_DRIVER]):
        print("--- DEBUG: One or more DB env vars missing! ---")
        print(f"DB_PROTOCOL: {'Set' if DB_PROTOCOL else 'MISSING'}")
        print(f"DB_USER: {'Set' if DB_USER else 'MISSING'}")
        print(f"DB_PASSWORD_RAW: {'Set' if DB_PASSWORD_RAW else 'MISSING'}")
        print(f"DB_SERVER: {'Set' if DB_SERVER else 'MISSING'}")
        print(f"DB_DATABASE: {'Set' if DB_DATABASE else 'MISSING'}")
        print(f"DB_DRIVER: {'Set' if DB_DRIVER else 'MISSING'}")
        raise ValueError("Missing one or more core database environment variables")

    # Construct DB URI only if not testing (and if all vars are present)
    SQLALCHEMY_DATABASE_URI = None
    if DB_PROTOCOL and DB_USER and DB_PASSWORD_RAW and DB_SERVER and DB_DATABASE and DB_DRIVER:
        DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD_RAW)
        query_params = {'driver': DB_DRIVER, 'Encrypt': 'yes', 'TrustServerCertificate': 'no'}
        query_string = urlencode(query_params)
        SQLALCHEMY_DATABASE_URI = (
            f"{DB_PROTOCOL}://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_SERVER}:{DB_PORT}/"
            f"{DB_DATABASE}?{query_string}"
        )
    elif not TESTING:
        print("Warning: Standard DB environment variables not fully set.")

    # --- Auth0 Config ---
    AUTH0_CLIENT_ID = os.environ.get('PROD_AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.environ.get('PROD_AUTH0_CLIENT_SECRET')
    AUTH0_DOMAIN = os.environ.get('PROD_AUTH0_DOMAIN')
    AUTH0_API_AUDIENCE = os.environ.get('PROD_AUTH0_API_AUDIENCE')

    # --- Redis Config ---
    CACHE_TYPE = os.getenv("PROD_CACHE_TYPE")
    CACHE_REDIS_SSL = os.getenv("PROD_CACHE_REDIS_SSL")
    CACHE_PROTOCOL = os.getenv("PROD_CACHE_PROTOCOL")
    CACHE_DEFAULT_TIMEOUT = os.getenv("PROD_CACHE_DEFAULT_TIMEOUT")
    CACHE_ACCESS_KEY = os.getenv("PROD_CACHE_ACCESS_KEY")
    CACHE_SERVER = os.getenv("PROD_CACHE_SERVER")
    CACHE_PORT = os.getenv("PROD_CACHE_PORT")
    ALGORITHMS = os.getenv("PROD_CACHE_ALGORITHMS")

    if not all([CACHE_TYPE, CACHE_REDIS_SSL, CACHE_PROTOCOL, CACHE_DEFAULT_TIMEOUT, CACHE_ACCESS_KEY, CACHE_SERVER, CACHE_PORT, ALGORITHMS]):
        print("--- DEBUG: One or more DB env vars missing! ---")
        print(f"CACHE_TYPE: {'Set' if CACHE_TYPE else 'MISSING'}")
        print(f"CACHE_REDIS_SSL: {'Set' if CACHE_REDIS_SSL else 'MISSING'}")
        print(f"CACHE_PROTOCOL: {'Set' if CACHE_PROTOCOL else 'MISSING'}")
        print(f"CACHE_DEFAULT_TIMEOUT: {'Set' if CACHE_DEFAULT_TIMEOUT else 'MISSING'}")
        print(f"CACHE_ACCESS_KEY: {'Set' if CACHE_ACCESS_KEY else 'MISSING'}")
        print(f"CACHE_SERVER: {'Set' if CACHE_SERVER else 'MISSING'}")
        print(f"CACHE_PORT: {'Set' if CACHE_PORT else 'MISSING'}")
        print(f"ALGORITHMS: {'Set' if ALGORITHMS else 'MISSING'}")
        raise ValueError("Missing one or more core Redis environment variables")

    CACHE_REDIS_URL = None
    if CACHE_PROTOCOL and CACHE_ACCESS_KEY and CACHE_SERVER and CACHE_PORT:
        DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD_RAW)
        query_params = {'driver': DB_DRIVER, 'Encrypt': 'yes', 'TrustServerCertificate': 'no'}
        query_string = urlencode(query_params)
        CACHE_REDIS_URL = (
            f"{CACHE_PROTOCOL}://:{CACHE_ACCESS_KEY}@{CACHE_SERVER}:{CACHE_PORT}/0"
        )

    if not TESTING and not all([AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN, AUTH0_API_AUDIENCE]):
        print("Warning: Auth0 environment variables not fully set.")

class TestingConfig():
    """Testing-specific configuration."""
    TESTING = True
    DEBUG = True

    # in-memory SQLite database for tests
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Define server name for testing exteral url gen
    SERVER_NAME = "localhost"

    # Caching for tests
    CACHE_TYPE = 'SimpleCache' # Use simplecache so tests dont need our external redis instance
    CACHE_DEFAULT_TIMEOUT = 300
    ALGORITHMS = ["RS256"]

    SECRET_KEY = 'test_secretkey' # Simple key adequate for tests
    # Dummy Auth0 values for testing config (mocks will bypass actual use)
    AUTH0_DOMAIN = "testing.auth0.com"
    AUTH0_CLIENT_ID = "test_client_id"
    AUTH0_CLIENT_SECRET = "test_client_secret"
    AUTH0_API_AUDIENCE = "test-api-audience"
    KID="test-kid-123"
    
    # Other
    WTF_CSRF_ENABLED = False
