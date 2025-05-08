from models.user import User
from app.extensions import db

def get_internal_user_id_from_auth0_sub(auth0_subject_id: str):
    """
    Retrieves the local Fintrack user ID based on the Auth0 subject ID.

    Args:
        auth0_subject_id: The 'sub' claim from the Auth0 token.

    Returns:
        The integer Fintrack user ID if found, otherwise None.
    """
    if not auth0_subject_id:
        return None

    internal_user = User.query.filter_by(auth0_subject=auth0_subject_id).first()

    if internal_user:
        return internal_user.id
    return None

def create_internal_user_from_auth0_sub(auth0_subject_id: str, email: str = None):
    if not auth0_subject_id:
        return None
    internal_user = User(auth0_subject=auth0_subject_id, email=email)
    db.session.add(internal_user)
    db.session.commit()

    return get_internal_user_id_from_auth0_sub(auth0_subject_id) 