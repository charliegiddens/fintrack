from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from flask_caching import Cache

db = SQLAlchemy()
oauth = OAuth()
cache = Cache()