import json # Keep if needed for debugging user data
from flask import (
    Blueprint, flash, redirect, render_template, session, url_for, current_app # Use current_app for config
)
from urllib.parse import quote_plus, urlencode

# Import extensions and models needed in the routes
from extensions import db, oauth
from models import User, Expense

# ... rest of your routes ...
# Make sure any logic querying or creating objects uses Expense class now


# Create a Blueprint instance
# 'main' is the name of the blueprint. It's used in url_for (e.g., 'main.home')
main_bp = Blueprint('main', __name__)

# --- Route Definitions ---
# Use @main_bp.route instead of @app.route

@main_bp.route("/")
def home():
    """Render the home page."""
    user_profile = session.get('user')
    pretty_profile = json.dumps(user_profile, indent=4) if user_profile else None # For display
    return render_template(
        "home.html",
        session=user_profile,
        pretty=pretty_profile,
    )

@main_bp.route("/login")
def login():
    """Redirect users to Auth0 login."""
    # Access the registered Auth0 provider via the oauth object
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for(".callback", _external=True) # url_for('.callback') refers to callback within this blueprint
    )

@main_bp.route("/callback", methods=["GET", "POST"])
def callback():
    """Handle the callback from Auth0 after login."""
    try:
        # Exchange the authorization code for an access token and user info
        token = oauth.auth0.authorize_access_token()
        user_info = token.get('userinfo')
        session["user"] = user_info  # Store raw Auth0 info

        # --- Find or Create User in DB ---
        auth0_sub = user_info.get('sub')
        if not auth0_sub:
            print("Error: Auth0 subject ID not found in token.")
            flash("Authentication failed: Missing user identifier.", "error")
            return redirect(url_for(".home")) # Redirect to home within this blueprint

        # Query your User table using db.session
        db_user = db.session.query(User).filter_by(auth0_subject=auth0_sub).first()

        if not db_user:
            print(f"Creating new user for sub: {auth0_sub}")
            new_user = User(
                auth0_subject=auth0_sub,
                email=user_info.get('email')
            )
            db.session.add(new_user)
            db.session.commit()
            db_user = new_user

        # Store Database User ID in Session
        session["db_user_id"] = db_user.id
        print(f"User logged in. Auth0 Sub: {auth0_sub}, DB User ID: {db_user.id}")
        flash("Login successful!", "success")
        return redirect(url_for(".dashboard")) # Redirect to dashboard within this blueprint

    except Exception as e:
        print(f"Error during callback: {e}")
        flash(f"Authentication failed: {e}", "error")
        session.clear()
        return redirect(url_for(".home"))

@main_bp.route("/dashboard")
def dashboard():
    """A protected route only accessible after login."""
    if 'user' not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for(".login")) # Redirect to login within this blueprint

    # User is logged in, render the dashboard
    # Display user info directly from session for now
    pretty_profile = json.dumps(session.get('user'), indent=4)
    return render_template(
        "dashboard.html",
        user=session.get('user'),
        pretty=pretty_profile, # Pass pretty printed data
    )


@main_bp.route("/logout")
def logout():
    """Log the user out."""
    # Clear the Flask session
    session.clear()
    # Use current_app.config to access configuration settings securely
    domain = current_app.config['AUTH0_DOMAIN']
    client_id = current_app.config['AUTH0_CLIENT_ID']
    return_to_url = url_for(".home", _external=True) # Redirect back home within this blueprint

    logout_url = (
        f"https://{domain}/v2/logout?"
        + urlencode(
            {
                "returnTo": return_to_url,
                "client_id": client_id,
            },
            quote_via=quote_plus,
        )
    )
    # Can't flash message after session clear, redirect happens immediately
    # flash("You have been logged out.", "info")
    return redirect(logout_url)