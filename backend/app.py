import os
import json
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, session, url_for
from authlib.integrations.flask_client import OAuth
from urllib.parse import quote_plus, urlencode
import requests

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")

# Initialize Authlib OAuth client
oauth = OAuth(app)

# Register Auth0 as an OAuth provider
oauth.register(
    "auth0",
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email", # Standard OIDC scopes
    },
    server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# Routes

@app.route("/")
def home():
    """Render the home page."""
    # Pass user profile data from session to template if available
    user_profile = session.get('user')
    # print(f"User session data: {user_profile}") # Debugging line
    return render_template(
        "home.html",
        session=user_profile,
    )

@app.route("/login")
def login():
    """Redirect users to Auth0 login."""
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    """Handle the callback from Auth0 after login."""
    try:
        # Exchange the authorization code for an access token and user info
        token = oauth.auth0.authorize_access_token()
        session["user"] = token.get('userinfo') # Store user info in the session
        # print(f"Callback successful, user info: {session['user']}") # Debugging line
        return redirect("/dashboard") # Redirect to a protected page
    except Exception as e:
        # Handle cases where token exchange fails (e.g., user denied access)
        print(f"Error during callback: {e}") # Log the error
        # Optionally flash a message to the user
        return redirect(url_for("home")) # Redirect home or to an error page

@app.route("/dashboard")
def dashboard():
    """A protected route only accessible after login."""
    user_profile = session.get('user')
    if not user_profile:
        # If user is not logged in, redirect to login page
        return redirect(url_for("login"))
    # User is logged in, render the dashboard
    return render_template(
        "dashboard.html",
        user=user_profile,
    )

@app.route("/logout")
def logout():
    """Log the user out."""
    # Clear the Flask session
    session.clear()
    # Redirect user to Auth0 logout endpoint
    domain = os.getenv("AUTH0_DOMAIN")
    client_id = os.getenv("AUTH0_CLIENT_ID")
    return_to_url = url_for("home", _external=True) # Where to redirect after logout

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
    return redirect(logout_url)

# --- Run the App ---
if __name__ == "__main__":
    # Use port 5000 for local development, matching Auth0 callback URL
    app.run(host="0.0.0.0", port=5000, debug=True) # debug=True for development