import requests
import json
from functools import wraps
from flask import request, current_app, jsonify, g
import jwt
from jwt.algorithms import RSAAlgorithm

from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidSignatureError,
    DecodeError,
    InvalidTokenError,
    PyJWKError
)

from .extensions import cache

# Auth Error Exception
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

# JWKS Handling
def get_jwks_from_auth0_uncached():
    auth0_domain = current_app.config["AUTH0_DOMAIN"]
    if not auth0_domain:
        current_app.logger.error("AUTH0_DOMAIN not configured.")
        raise AuthError({"code": "config_error",
                         "description": "Authentication service domain not configured."}, 500)

    current_app.logger.info(f"Fetching JWKS from Auth0 (https://{auth0_domain}/.well-known/jwks.json) (not from cache)...")
    try:
        jwks_url = f"https://{auth0_domain}/.well-known/jwks.json"
        jwks_response = requests.get(jwks_url, timeout=10)
        jwks_response.raise_for_status()
        jwks = jwks_response.json()
        if not jwks or "keys" not in jwks:
            current_app.logger.error(f"Invalid JWKS format received from {jwks_url}")
            raise AuthError({"code": "jwks_invalid_format",
                             "description": "Invalid JWKS format received."}, 500)
        return jwks
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error fetching JWKS: {e}")
        raise AuthError({"code": "jwks_fetch_error",
                         "description": "Unable to fetch JWKS."}, 500)

# JWT Verification
def get_token_auth_header():
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description": "Authorization header is expected"}, 401)
    parts = auth.split()
    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description": "Authorization header must start with 'Bearer'"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header", "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description": "Authorization header must be Bearer token"}, 401)
    return parts[1]

def verify_decode_jwt(token, jwks):
    try:
        unverified_header = jwt.get_unverified_header(token)
    except DecodeError as e:
        current_app.logger.warning(f"Invalid token header: {e}")
        raise AuthError({"code": "invalid_header",
                        "description": f"Invalid token header: {str(e)}"}, 401)

    if 'kid' not in unverified_header:
        raise AuthError({"code": "invalid_header",
                        "description": "Authorization malformed. 'kid' missing from header."}, 401)

    rsa_key_dict = None
    for key_component in jwks["keys"]:
        if key_component["kid"] == unverified_header["kid"]:
            rsa_key_dict = key_component # Stores the whole key dict
            break

    if not rsa_key_dict:
        raise AuthError({"code": "invalid_key",
                        "description": "Unable to find appropriate key in JWKS for token verification."}, 401)

    try:
        public_key = RSAAlgorithm.from_jwk(json.dumps(rsa_key_dict))
    except PyJWKError as e:
        current_app.logger.error(f"Error constructing public key from JWK: {e}")
        raise AuthError({"code": "key_construction_error",
                         "description": "Could not construct public key from JWK."}, 500)
    except Exception as e:
        current_app.logger.error(f"Unexpected error constructing public key: {e}", exc_info=True)
        raise AuthError({"code": "key_construction_error",
                         "description": "Unexpected error during public key construction."}, 500)


    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=current_app.config["ALGORITHMS"],
            audience=current_app.config["AUTH0_API_AUDIENCE"],
            issuer=f"https://{current_app.config['AUTH0_DOMAIN']}/"
        )
        return payload

    except ExpiredSignatureError:
        current_app.logger.warning("Token is expired.")
        raise AuthError({"code": "token_expired", "description": "Token is expired."}, 401)
    except InvalidAudienceError:
        current_app.logger.warning("Incorrect audience.")
        raise AuthError({"code": "invalid_audience",
                        "description": "Incorrect audience, please check the API_AUDIENCE setting."}, 401)
    except InvalidIssuerError:
        current_app.logger.warning("Incorrect issuer.")
        raise AuthError({"code": "invalid_issuer",
                        "description": "Incorrect issuer, please check the AUTH0_DOMAIN setting."}, 401)
    except InvalidSignatureError:
        current_app.logger.warning("Invalid token signature.")
        raise AuthError({"code": "invalid_signature",
                        "description": "Token signature verification failed."}, 401)
    except DecodeError as e:
        current_app.logger.warning(f"Token decode error: {e}")
        raise AuthError({"code": "token_decode_error",
                        "description": "Token is malformed or could not be decoded."}, 401)
    except InvalidTokenError as e:
        current_app.logger.warning(f"Invalid token: {e}")
        raise AuthError({"code": "invalid_token",
                        "description": f"Invalid token: {str(e)}"}, 401)
    except Exception as e:
        current_app.logger.error(f"Unexpected error decoding JWT: {e}", exc_info=True)
        raise AuthError({"code": "jwt_decode_unexpected_error",
                        "description": "An unexpected error occurred while decoding the token."}, 500)


# requires_auth decorator
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        memoized_get_jwks = cache.memoize(timeout=current_app.config['CACHE_DEFAULT_TIMEOUT'])(get_jwks_from_auth0_uncached)
        try:
            token = get_token_auth_header()
            jwks = memoized_get_jwks()
            if not jwks:
                raise AuthError({"code": "jwks_unavailable",
                                 "description": "JWKS not available for token validation."}, 500)
            payload = verify_decode_jwt(token, jwks)
            g.current_user = payload
        except AuthError as e:
            raise e
        except Exception as ex:
            current_app.logger.error(f"Unexpected error in requires_auth decorator: {ex}", exc_info=True)
            raise AuthError({"code": "internal_server_error",
                             "description": "An unexpected error occurred during authentication processing."}, 500)
        return f(*args, **kwargs)
    return decorated

def clear_jwks_cache_util():
    memoized_get_jwks = cache.memoize(timeout=current_app.config['CACHE_DEFAULT_TIMEOUT'])(get_jwks_from_auth0_uncached)
    cache.delete_memoized(memoized_get_jwks)
    current_app.logger.info("JWKS cache cleared via utility function.")