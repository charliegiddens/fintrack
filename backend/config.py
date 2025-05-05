# config.py
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus, urlencode

# Load environment variables from .env file into the environment
load_dotenv()

class Config:
    """Base configuration variables."""
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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

    # URL-encode password
    DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD_RAW)

    query_params = {
        'driver': DB_DRIVER,
        'Encrypt': 'yes',
        'TrustServerCertificate': 'no',
    }
    # Encode the parameters into a query string (e.g., driver=...&Encrypt=yes...)
    query_string = urlencode(query_params)

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_SERVER}:{DB_PORT}/"
        f"{DB_DATABASE}?{query_string}"
    )

    # --- Debug Print ---
    print("--- DEBUG (DSN Params in URL Query) ---")
    print(f"SQLALCHEMY_DATABASE_URI (Password Hidden): mssql+pyodbc://{DB_USER}:<PASSWORD_HIDDEN>@{DB_SERVER}:{DB_PORT}/{DB_DATABASE}?{query_string}")
    print(f"Actual URI is set: {bool(SQLALCHEMY_DATABASE_URI)}")
    print("--- END DEBUG ---")

    # --- Auth0 Config ---
    AUTH0_CLIENT_ID = os.environ.get('AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.environ.get('AUTH0_CLIENT_SECRET')
    AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN')

    if not all([AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_DOMAIN]):
        raise ValueError("Missing one or more Auth0 environment variables")