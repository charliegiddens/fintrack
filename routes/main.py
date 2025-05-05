import json
from flask import Blueprint, render_template, session, redirect, url_for, flash
from models import User # Assuming you might need User details later

# Define the Blueprint for main pages
main_bp = Blueprint(
    'main',
    __name__,
    template_folder='../templates' # Point to the main templates folder
)

@main_bp.route("/")
def home():
    user_profile = session.get('user')
    pretty_profile = json.dumps(user_profile, indent=4) if user_profile else None
    return render_template(
        "home.html",
        user=user_profile, 
        pretty=pretty_profile
    )

@main_bp.route("/dashboard")
def dashboard():
    """A protected route only accessible after login."""
    if 'user' not in session:
        flash("Please log in to access the dashboard.", "warning")
        # Need to link to the login route in the 'auth' blueprint
        return redirect(url_for("auth.login"))

    pretty_profile = json.dumps(session.get('user'), indent=4)
    return render_template(
        "dashboard.html",
        user=session.get('user'),
        pretty=pretty_profile,
    )