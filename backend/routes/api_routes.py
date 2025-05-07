from flask import Blueprint, jsonify, g
from app.auth_utils import requires_auth
from app.api_helpers import get_internal_user_id_from_auth0_sub

api_bp = Blueprint('api', __name__)

@api_bp.route("/public")
def public_endpoint():
    return jsonify(message="Hello from a public endpoint! You don't need to be authenticated.")

@api_bp.route("/private")
@requires_auth
def private_endpoint():
    if hasattr(g, 'current_user'):
        user_payload = g.current_user
        auth0_subject_id = user_payload.get("sub")
        local_user_id = get_internal_user_id_from_auth0_sub(auth0_subject_id)

        return jsonify(message=f"Auth0 User ID: {auth0_subject_id} | Fintrack User ID: {local_user_id}")

# Commenting this code out ready for when we start adding scoped endpoints

# @api_bp.route("/private-scoped")
# @requires_auth
# def private_scoped_endpoint():
#     # Boilerplate code for when we add scoping to private endpoins
#     # if hasattr(g, 'current_user'):
#     #    user_payload = g.current_user
#     #    required_scope = "read:messages"
#     #    if required_scope not in user_payload.get("permissions", []): # Auth0 often uses 'permissions' for scopes
#     #        raise AuthError({"code": "insufficient_scope",
#     #                         "description": f"Requires '{required_scope}' scope."}, 403)
#     return jsonify(message="Hello from a private scoped endpoint! You are authenticated (scope check would go here).")

# @api_bp.route("/clear-cache", methods=['POST'])
# @requires_auth
# def clear_cache_endpoint():
#     # Example admin check:
#     # if hasattr(g, 'current_user'):
#     #    user_payload = g.current_user
#     #    if "admin:cache" not in user_payload.get("permissions", []):
#     #        raise AuthError({"code": "forbidden", "description": "Admin privileges required."}, 403)
#     try:
#         clear_jwks_cache_util()
#         return jsonify(message="JWKS cache successfully cleared."), 200
#     except Exception as e:
#         current_app.logger.error(f"Error clearing cache: {e}", exc_info=True)
#         return jsonify(error="Failed to clear cache", details=str(e)), 500