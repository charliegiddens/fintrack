import os
from dotenv import load_dotenv
from urllib.parse import quote_plus, urlencode

load_dotenv()

class Config:
    TESTING = False
    SECRET_KEY = os.getenv('APP_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis
    CACHE_PROTOCOL = os.getenv("CACHE_PROTOCOL")
    CACHE_TYPE = os.getenv("CACHE_TYPE")
    CACHE_REDIS_SSL = os.getenv("CACHE_REDIS_SSL")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT"))
    ALGORITHMS = os.getenv("CACHE_ALGORITHMS")
    CACHE_USER = os.getenv("CACHE_USER")
    CACHE_PASS = os.getenv("CACHE_PASS")
    CACHE_HOST = os.getenv("CACHE_HOST")
    CACHE_PORT = os.getenv("CACHE_PORT")
    CACHE_REDIS_URL = (
        f"{CACHE_PROTOCOL}://{CACHE_USER}:{CACHE_PASS}@{CACHE_HOST}:{CACHE_PORT}"
        if all((CACHE_USER, CACHE_PASS, CACHE_HOST, CACHE_PORT)) else None
    )

    # SQLAlchemy URI
    DB_PROTOCOL = os.getenv("DB_PROTOCOL")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    SQLALCHEMY_DATABASE_URI = (
        f"{DB_PROTOCOL}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}" 
        if all((DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME)) else None
    )

    # Auth0
    AUTH0_CLIENT_ID = os.getenv('AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.getenv('AUTH0_CLIENT_SECRET')
    AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
    AUTH0_API_AUDIENCE = os.getenv('AUTH0_API_AUDIENCE')

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
