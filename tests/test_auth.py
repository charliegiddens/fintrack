import pytest
import pytest_mock
from flask import url_for, session as flask_session, redirect
from models import User
from extensions import oauth

# Use 'mocker' fixture provided by pytest-mock
def test_login_redirects_to_auth0(client, mocker):
    """Test that /login route calls Auth0's authorize_redirect."""
    # Mock the actual method call on the oauth object used by the app
    mock_authorize = mocker.patch.object(oauth.auth0, 'authorize_redirect', autospec=True)
    # Define what the mock should return (e.g., a simple response or redirect object)
    # Often mocking it to return a simple string/response is enough to check it was called
    mock_authorize.return_value = redirect(url_for('main.home')) # Dummy redirect

    response = client.get(url_for('auth.login'))

    # Assert our mock was called exactly once with the expected redirect_uri
    mock_authorize.assert_called_once()
    # Check the argument passed to the mock (it's a dict-like object)
    args, kwargs = mock_authorize.call_args
    assert 'redirect_uri' in kwargs
    assert kwargs['redirect_uri'] == url_for('auth.callback', _external=True)
    # assert response.status_code == 302 # If mock returned a real redirect

def test_callback_new_user(client, session, mocker): # Use the db session fixture
    """Test the /callback route when a new user logs in."""

    # 1. Mock Auth0 token exchange
    mock_authorize_token = mocker.patch.object(oauth.auth0, 'authorize_access_token', autospec=True)
    mock_authorize_token.return_value = {
        'access_token': 'dummy_access_token', 'token_type': 'Bearer',
        'userinfo': {
            'sub': 'auth0|newuser123', 'name': 'Test New User',
            'email': 'new.user@example.com', 'email_verified': True
        }
    }

    # 2. Make the request
    response = client.get(url_for('auth.callback'), follow_redirects=True)

    # 3. Assertions
    assert response.status_code == 200
    assert b"Dashboard" in response.data

    # Check database using the db session fixture
    user = session.query(User).filter_by(auth0_subject='auth0|newuser123').first()
    assert user is not None
    assert user.email == 'new.user@example.com'

    # --- Check Flask's session via the client AFTER the request ---
    # The client stores the session cookies from the response
    # Accessing session state requires being inside a request or using the client
    # Note: Direct access to client.session_transaction might not reflect final state easily after redirects.
    # A better way is often to make another request to a protected endpoint
    # that relies on the session being set correctly.

    # Option A: Check a protected route (Recommended)
    # Make a subsequent request to the dashboard AFTER the callback logic ran
    dashboard_response = client.get(url_for('main.dashboard'))
    assert dashboard_response.status_code == 200