from models.user import User
from app.extensions import db

def get_or_create_internal_user_id(auth0_subject_id: str, email: str = None, create_if_missing: bool = False):
    """
    Retrieves the local Fintrack user ID based on the Auth0 subject ID.
    Optionally creates the user if not found and `create_if_missing` is True.

    Args:
        auth0_subject_id: The 'sub' claim from the Auth0 token.
        email: Optional email to use if user needs to be created.
        create_if_missing: Whether to create the user if not found.

    Returns:
        The integer Fintrack user ID if found or created, otherwise None.
    """
    if not auth0_subject_id:
        return None

    internal_user = User.query.filter_by(auth0_subject=auth0_subject_id).first()
    if internal_user:
        return internal_user.id

    if create_if_missing:
        new_user = User(auth0_subject=auth0_subject_id, email=email)
        db.session.add(new_user)
        db.session.commit()
        return new_user.id

    return None
