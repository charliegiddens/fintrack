import pytest
from flask import g as flask_g, current_app as flask_current_app

from app.auth_utils import (
    AuthError,
    requires_auth
)

from tests.conftest import SAMPLE_JWKS, SAMPLE_PAYLOAD, TEST_TOKEN

# # --- Mock Fixtures for requires_auth dependencies ---
# @pytest.fixture
# def mock_get_token_auth_header(mocker):
#     """Mocks app.auth_utils.get_token_auth_header"""
#     return mocker.patch('app.auth_utils.get_token_auth_header')

# @pytest.fixture
# def mock_get_jwks_from_auth0_uncached(mocker):
#     """Mocks app.auth_utils.get_jwks_from_auth0_uncached"""
#     return mocker.patch('app.auth_utils.get_jwks_from_auth0_uncached')

# @pytest.fixture
# def mock_verify_decode_jwt(mocker):
#     """Mocks app.auth_utils.verify_decode_jwt"""
#     return mocker.patch('app.auth_utils.verify_decode_jwt')


# --- Tests for requires_auth decorator ---
def test_requires_auth_success(
    app_context, request_context, # Flask contexts
    mock_auth_utils_cache,      # Cache mock from conftest
    mock_get_token_auth_header,
    mock_get_jwks_from_auth0_uncached,
    mock_verify_decode_jwt
):
    """Test successful authentication flow through requires_auth."""
    mock_get_token_auth_header.return_value = TEST_TOKEN
    # The memoized function will call the uncached one, which our mock_auth_utils_cache ensures
    mock_get_jwks_from_auth0_uncached.return_value = SAMPLE_JWKS
    mock_verify_decode_jwt.return_value = SAMPLE_PAYLOAD

    @requires_auth
    def protected_route():
        return "Authenticated", 200

    response, status_code = protected_route()

    assert response == "Authenticated"
    assert status_code == 200
    assert flask_g.current_user == SAMPLE_PAYLOAD

    mock_get_token_auth_header.assert_called_once()
    # cache.memoize is called once by requires_auth to create memoized_get_jwks
    mock_auth_utils_cache.memoize.assert_called_once_with(timeout=flask_current_app.config['CACHE_DEFAULT_TIMEOUT'])
    # The (mocked) uncached function is called once via the memoized wrapper
    mock_get_jwks_from_auth0_uncached.assert_called_once()
    mock_verify_decode_jwt.assert_called_once_with(TEST_TOKEN, SAMPLE_JWKS)


def test_requires_auth_raises_auth_error_from_dependency(
    app_context, request_context,
    mock_auth_utils_cache,
    mock_get_token_auth_header
    # Other mocks not needed if get_token_auth_header fails early
):
    """Test that AuthError from a dependency is re-raised by requires_auth."""
    expected_error = AuthError({"code": "test_err", "description": "Test Error"}, 401)
    mock_get_token_auth_header.side_effect = expected_error

    @requires_auth
    def protected_route():
        return "Should not reach here"

    with pytest.raises(AuthError) as exc_info:
        protected_route()

    assert exc_info.value == expected_error # Checks if the exact exception instance is raised
    mock_get_token_auth_header.assert_called_once()
    mock_auth_utils_cache.memoize.assert_called_once_with(timeout=flask_current_app.config['CACHE_DEFAULT_TIMEOUT'])


def test_requires_auth_jwks_unavailable(
    app_context, request_context,
    mock_auth_utils_cache,
    mock_get_token_auth_header,
    mock_get_jwks_from_auth0_uncached
):
    """Test requires_auth when JWKS are not available (returns None)."""
    mock_get_token_auth_header.return_value = TEST_TOKEN