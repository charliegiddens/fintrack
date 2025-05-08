from unittest.mock import MagicMock

from app.api_helpers import get_internal_user_id_from_auth0_sub

def test_get_internal_user_id_with_none_auth0_id():
    """Test that providing None for auth0_subject_id returns None."""
    assert get_internal_user_id_from_auth0_sub(None) is None

def test_get_internal_user_id_with_empty_auth0_id():
    """Test that providing an empty string for auth0_subject_id returns None."""
    assert get_internal_user_id_from_auth0_sub("") is None

def test_get_internal_user_id_user_found(mocker):
    """Test the case where a user is found for the given auth0_subject_id."""

    mock_user_instance = MagicMock()
    mock_user_instance.id = 123

    # This mock_User_class will replace the User class within api_helpers.py
    mock_User_class = mocker.patch('app.api_helpers.User')

    # This just replicates our 'User.query.filter_by(...).first()', which should return mock_user_instance
    mock_User_class.query.filter_by.return_value.first.return_value = mock_user_instance

    auth0_id = "auth0|some_valid_subject"
    result = get_internal_user_id_from_auth0_sub(auth0_id)

    assert result == 123

    mock_User_class.query.filter_by.assert_called_once_with(auth0_subject=auth0_id)
    mock_User_class.query.filter_by.return_value.first.assert_called_once()

def test_get_internal_user_id_user_not_found(mocker):
    """Test the case where no user is found for the given auth0_subject_id."""

    mock_User_class = mocker.patch('app.api_helpers.User')

    mock_User_class.query.filter_by.return_value.first.return_value = None

    auth0_id = "auth0|some_nonexistent_subject"
    result = get_internal_user_id_from_auth0_sub(auth0_id)

    assert result is None

    mock_User_class.query.filter_by.assert_called_once_with(auth0_subject=auth0_id)
    mock_User_class.query.filter_by.return_value.first.assert_called_once()