# routes/auth.py
from flask import (
    Blueprint, redirect, url_for, session, current_app, flash
)
from urllib.parse import quote_plus, urlencode
from extensions import db, oauth # Need db and oauth
from models import User # Need User model for callback

# Define the Blueprint for authentication routes
auth_bp = Blueprint(
    'auth',
    __name__,
    template_folder='../templates' # Point to the main templates folder
    # url_prefix='/auth' # Optional: Prefix all routes in this blueprint
)

@auth_bp.route("/login")
def login():
    """Redirect users to Auth0 login."""
    return oauth.auth0.authorize_redirect(
        # Callback is within this blueprint, use relative '.'
        redirect_uri=url_for(".callback", _external=True)
    )

@auth_bp.route("/callback", methods=["GET", "POST"])
def callback():
    """Handle the callback from Auth0 after login."""
    try:
        token = oauth.auth0.authorize_access_token()
        user_info = token.get('userinfo')
        session["user"] = user_info

        auth0_sub = user_info.get('sub')
        if not auth0_sub:
            print("Error: Auth0 subject ID not found.")
            flash("Authentication failed: Missing user identifier.", "error")
            # Redirect to home route in the 'main' blueprint
            return redirect(url_for("main.home"))

        db_user = db.session.query(User).filter_by(auth0_subject=auth0_sub).first()
        if not db_user:
            print(f"Creating new user for sub: {auth0_sub}")
            new_user = User(auth0_subject=auth0_sub, email=user_info.get('email'))
            db.session.add(new_user)
            db.session.commit()
            db_user = new_user

        session["db_user_id"] = db_user.id
        print(f"User logged in. Auth0 Sub: {auth0_sub}, DB User ID: {db_user.id}")
        # Redirect to dashboard route in the 'main' blueprint
        return redirect(url_for("main.dashboard"))

    except Exception as e:
        print(f"Error during callback: {e}")
        flash(f"Authentication failed: {e}", "error")
        session.clear()
        return redirect(url_for("main.home"))

@auth_bp.route("/logout")
def logout():
    """Log the user out."""
    session.clear()
    domain = current_app.config['AUTH0_DOMAIN']
    client_id = current_app.config['AUTH0_CLIENT_ID']
    # Redirect to home route in the 'main' blueprint after logout
    return_to_url = url_for("main.home", _external=True)

    logout_url = (
        f"https://{domain}/v2/logout?"
        + urlencode({"returnTo": return_to_url, "client_id": client_id,}, quote_via=quote_plus)
    )
    return redirect(logout_url)