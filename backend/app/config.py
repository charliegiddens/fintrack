import os
from dotenv import load_dotenv
from urllib.parse import quote_plus, urlencode

load_dotenv()

class DevelopmentConfig:
    TESTING = False
    SECRET_KEY = os.getenv('DEV_APP_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = os.getenv('DEV_FRONTEND_ORIGIN')
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DB_URI")

    # Redis
    CACHE_TYPE = os.getenv("DEV_CACHE_TYPE")
    CACHE_DEFAULT_TIMEOUT = 300

    # Auth0
    AUTH0_CLIENT_ID = os.getenv('DEV_AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.getenv('DEV_AUTH0_CLIENT_SECRET')
    AUTH0_DOMAIN = os.getenv('DEV_AUTH0_DOMAIN')
    AUTH0_API_AUDIENCE = os.getenv('DEV_AUTH0_API_AUDIENCE')


class StagingConfig:
    TESTING = False
    SECRET_KEY = os.getenv('STAGING_APP_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FRONTEND_ORIGIN = os.getenv('STAGING_FRONTEND_ORIGIN')

    # Auth0
    AUTH0_CLIENT_ID = os.getenv('STAGING_AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.getenv('STAGING_AUTH0_CLIENT_SECRET')
    AUTH0_DOMAIN = os.getenv('STAGING_AUTH0_DOMAIN')
    AUTH0_API_AUDIENCE = os.getenv('STAGING_AUTH0_API_AUDIENCE')

    # Redis
    CACHE_TYPE = os.getenv("STAGING_CACHE_TYPE")
    CACHE_REDIS_SSL = os.getenv("STAGING_CACHE_REDIS_SSL")
    CACHE_PROTOCOL = os.getenv("STAGING_CACHE_PROTOCOL")
    CACHE_DEFAULT_TIMEOUT = os.getenv("STAGING_CACHE_DEFAULT_TIMEOUT")
    CACHE_ACCESS_KEY = os.getenv("STAGING_CACHE_ACCESS_KEY")
    CACHE_SERVER = os.getenv("STAGING_CACHE_SERVER")
    CACHE_PORT = os.getenv("STAGING_CACHE_PORT")
    ALGORITHMS = os.getenv("STAGING_CACHE_ALGORITHMS")

    # SQLAlchemy URI
    _DB_PROTOCOL = os.getenv('STAGING_DB_PROTOCOL')
    _DB_USER = os.getenv('STAGING_DB_USER')
    _DB_PASSWORD = quote_plus(os.getenv('STAGING_DB_PASSWORD', ''))
    _DB_SERVER = os.getenv('STAGING_DB_SERVER')
    _DB_PORT = os.getenv('STAGING_DB_PORT')
    _DB_DATABASE = os.getenv('STAGING_DB_DATABASE')
    _DB_DRIVER = os.getenv('STAGING_DB_DRIVER')
    _DB_QUERY = urlencode({'driver': _DB_DRIVER, 'Encrypt': 'yes', 'TrustServerCertificate': 'no'})

    SQLALCHEMY_DATABASE_URI = (
        f"{_DB_PROTOCOL}://{_DB_USER}:{_DB_PASSWORD}@{_DB_SERVER}:{_DB_PORT}/{_DB_DATABASE}?{_DB_QUERY}"
        if all([_DB_PROTOCOL, _DB_USER, _DB_PASSWORD, _DB_SERVER, _DB_PORT, _DB_DATABASE, _DB_DRIVER])
        else None
    )


class ProductionConfig(StagingConfig):
    """Same structure as staging, just reads from PROD_ vars."""

    SECRET_KEY = os.getenv('PROD_APP_SECRET_KEY')
    FRONTEND_ORIGIN = os.getenv('PROD_FRONTEND_ORIGIN')

    AUTH0_CLIENT_ID = os.getenv('PROD_AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.getenv('PROD_AUTH0_CLIENT_SECRET')
    AUTH0_DOMAIN = os.getenv('PROD_AUTH0_DOMAIN')
    AUTH0_API_AUDIENCE = os.getenv('PROD_AUTH0_API_AUDIENCE')

    CACHE_TYPE = os.getenv("PROD_CACHE_TYPE")
    CACHE_REDIS_SSL = os.getenv("PROD_CACHE_REDIS_SSL")
    CACHE_PROTOCOL = os.getenv("PROD_CACHE_PROTOCOL")
    CACHE_DEFAULT_TIMEOUT = os.getenv("PROD_CACHE_DEFAULT_TIMEOUT")
    CACHE_ACCESS_KEY = os.getenv("PROD_CACHE_ACCESS_KEY")
    CACHE_SERVER = os.getenv("PROD_CACHE_SERVER")
    CACHE_PORT = os.getenv("PROD_CACHE_PORT")
    ALGORITHMS = os.getenv("PROD_CACHE_ALGORITHMS")

    _DB_PROTOCOL = os.getenv('PROD_DB_PROTOCOL')
    _DB_USER = os.getenv('PROD_DB_USER')
    _DB_PASSWORD = quote_plus(os.getenv('PROD_DB_PASSWORD', ''))
    _DB_SERVER = os.getenv('PROD_DB_SERVER')
    _DB_PORT = os.getenv('PROD_DB_PORT')
    _DB_DATABASE = os.getenv('PROD_DB_DATABASE')
    _DB_DRIVER = os.getenv('PROD_DB_DRIVER')
    _DB_QUERY = urlencode({'driver': _DB_DRIVER, 'Encrypt': 'yes', 'TrustServerCertificate': 'no'})

    SQLALCHEMY_DATABASE_URI = (
        f"{_DB_PROTOCOL}://{_DB_USER}:{_DB_PASSWORD}@{_DB_SERVER}:{_DB_PORT}/{_DB_DATABASE}?{_DB_QUERY}"
        if all([_DB_PROTOCOL, _DB_USER, _DB_PASSWORD, _DB_SERVER, _DB_PORT, _DB_DATABASE, _DB_DRIVER])
        else None
    )


class TestingConfig:
    TESTING = True
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SERVER_NAME = "localhost"
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    ALGORITHMS = ["RS256"]
    SECRET_KEY = 'test_secretkey'
    AUTH0_DOMAIN = "testing.auth0.com"
    AUTH0_CLIENT_ID = "test_client_id"
    AUTH0_CLIENT_SECRET = "test_client_secret"
    AUTH0_API_AUDIENCE = "test-api-audience"
    KID = "test-kid-123"
    WTF_CSRF_ENABLED = False
