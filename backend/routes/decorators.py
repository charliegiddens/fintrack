import jwt
import requests
from functools import wraps
from flask import request, jsonify, current_app

from models import User
from extensions import db, cache

class AuthError(Exception):
    def __init__(self, error_payload, status_code):
        super().__init__(error_payload.get("description", "Authentication Error"))
        self.error_payload = error_payload
        self.status_code = status_code

# JWKS Caching Configuration
JWKS_CACHE_KEY = 'auth0_jwks_keys_v1'
JWKS_CACHE_TIMEOUT = 3600 * 24 # 24h

def get_jwks():
    """
    Fetches and caches the JSON Web Key Set (JWKS) from the Auth0 domain using Flask-Caching.
    """
    auth0_domain = current_app.config.get('AUTH0_DOMAIN')
    if not auth0_domain:
        current_app.logger.error("AUTH0_DOMAIN not configured.")
        raise AuthError({"code": "config_error", "description": "Authentication service not configured."}, 500)

    jwks_url = f"https://{auth0_domain}/.well-known/jwks.json"

    # Try to get JWKS from cache
    cached_jwks_keys = cache.get(JWKS_CACHE_KEY)
    if cached_jwks_keys:
        current_app.logger.debug(f"JWKS retrieved from cache (key: {JWKS_CACHE_KEY}).")
        return cached_jwks_keys

    # If not in cache, fetch from Auth0
    try:
        current_app.logger.info(f"Fetching JWKS from {jwks_url} (cache miss for key: {JWKS_CACHE_KEY}).")
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        jwks_data = response.json()
        jwks_keys = jwks_data.get("keys")

        if not jwks_keys:
            current_app.logger.error("JWKS fetched successfully but 'keys' array is missing or empty.")
            raise AuthError({"code": "jwks_format_error", "description": "Invalid JWKS format received."}, 500)

        # Store fetched JWKS in cache with a specific timeout
        cache.set(JWKS_CACHE_KEY, jwks_keys, timeout=JWKS_CACHE_TIMEOUT)
        current_app.logger.info(f"JWKS cached (key: {JWKS_CACHE_KEY}, timeout: {JWKS_CACHE_TIMEOUT}s).")
        return jwks_keys

    except requests.exceptions.Timeout:
        current_app.logger.error(f"Timeout while fetching JWKS from {jwks_url}.")
        raise AuthError({"code": "jwks_timeout", "description": "Timeout connecting to authentication key server."}, 503)
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Failed to fetch JWKS: {e}")
        raise AuthError({"code": "jwks_fetch_error", "description": "Unable to fetch public keys for token validation."}, 500)
    except ValueError as e: # Includes JSONDecodeError
        current_app.logger.error(f"Failed to decode JWKS JSON: {e}")
        raise AuthError({"code": "jwks_decode_error", "description": "Unable to parse public key information."}, 500)

def get_signing_key(token):
    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as e:
        current_app.logger.warning(f"Invalid token header: {e}")
        raise AuthError({"code": "invalid_header", "description": f"Invalid token header: {str(e)}"}, 401)

    if 'kid' not in unverified_header:
        raise AuthError({"code": "invalid_header", "description": "Token header missing 'kid' (Key ID)."}, 401)

    kid = unverified_header['kid']
    jwks_keys = get_jwks() # This will now use the cached version
    rsa_key_dict = {}

    for key in jwks_keys:
        if key.get("kid") == kid:
            if key.get("kty") != "RSA" or key.get("use") != "sig":
                current_app.logger.warning(f"Key with KID {kid} found but not a valid RSA signing key.")
                continue
            rsa_key_dict = {
                "kty": key.get("kty"), "kid": key.get("kid"), "use": key.get("use"),
                "n": key.get("n"), "e": key.get("e")
            }
            break

    if not rsa_key_dict:
        current_app.logger.warning(f"RSA signing key with KID {kid} not found in JWKS.")
        raise AuthError({"code": "signing_key_not_found", "description": "Unable to find appropriate signing key for token."}, 401)

    try:
        return jwt.algorithms.RSAAlgorithm.from_jwk(rsa_key_dict)
    except jwt.PyJWTError as e:
        current_app.logger.error(f"Could not construct RSA signing key from JWK: {e}")
        raise AuthError({"code": "key_construction_error", "description": "Error processing signing key."}, 500)

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return jsonify({"code": "authorization_header_missing",
                            "description": "Authorization header is expected."}), 401

        parts = auth_header.split()
        if parts[0].lower() != 'bearer':
            return jsonify({"code": "invalid_header",
                            "description": "Authorization header must start with 'Bearer'."}), 401
        elif len(parts) == 1:
            return jsonify({"code": "invalid_header", "description": "Token not found after 'Bearer'."}), 401
        elif len(parts) > 2:
            return jsonify({"code": "invalid_header", "description": "Authorization header must be 'Bearer <token>'."}), 401

        token = parts[1]

        try:
            signing_key = get_signing_key(token)

            api_audience = current_app.config.get('AUTH0_API_AUDIENCE')
            issuer = f"https://{current_app.config.get('AUTH0_DOMAIN')}/"

            if not api_audience or not current_app.config.get('AUTH0_DOMAIN'):
                current_app.logger.error("AUTH0_API_AUDIENCE or AUTH0_DOMAIN not configured for token validation.")
                raise AuthError({"code": "config_error", "description": "API authentication parameters not configured."}, 500)

            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=api_audience,
                issuer=issuer
            )
        except AuthError as e:
            return jsonify(e.error_payload), e.status_code
        except jwt.ExpiredSignatureError:
            return jsonify({"code": "token_expired", "description": "Token has expired."}), 401
        except jwt.InvalidAudienceError:
            return jsonify({"code": "invalid_audience", "description": "Token has an invalid audience."}), 401
        except jwt.InvalidIssuerError:
            return jsonify({"code": "invalid_issuer", "description": "Token has an invalid issuer."}), 401
        except jwt.PyJWTError as e:
            current_app.logger.warning(f"JWT validation error: {e}")
            return jsonify({"code": "invalid_token", "description": f"Token is invalid: {str(e)}"}), 401
        except Exception as e:
            current_app.logger.error(f"Unexpected error during token decoding: {e}", exc_info=True)
            return jsonify({"code": "token_processing_error", "description": "Error processing token."}), 500

        auth0_sub = payload.get('sub')
        if not auth0_sub:
            return jsonify({"code": "invalid_claims", "description": "'sub' claim missing from token."}), 401

        current_user = db.session.query(User).filter_by(auth0_subject=auth0_sub).first()
        if not current_user:
            current_app.logger.info(f"User with sub {auth0_sub} not found in local database.")
            return jsonify({"code": "user_not_found", "description": "User identified by token not found in application database."}), 403

        return f(current_user, *args, **kwargs)

    return decorated_function