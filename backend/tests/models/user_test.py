import pytest
from sqlalchemy.exc import IntegrityError

from models.user import User
from models.expense import Expense # For testing relationships

def test_create_user(db):
    """Test creating a new User instance."""
    auth0_id = "auth0|testsubject123"
    email_addr = "test@example.com"
    user = User(auth0_subject=auth0_id, email=email_addr)

    db.session.add(user)
    db.session.commit()

    assert user.id is not None
    assert user.auth0_subject == auth0_id
    assert user.email == email_addr

    retrieved_user = db.session.get(User, user.id)
    assert retrieved_user is not None
    assert retrieved_user.auth0_subject == auth0_id

def test_user_repr_with_email(db):
    """Test the __repr__ method of User when email is present."""
    user = User(auth0_subject="auth0|repr1", email="repr@example.com")
    db.session.add(user)
    db.session.commit()
    assert repr(user) == "<User repr@example.com>"

def test_user_repr_without_email(db):
    """Test the __repr__ method of User when email is None."""
    user = User(auth0_subject="auth0|repr2")
    db.session.add(user)
    db.session.commit()
    assert repr(user) == "<User auth0|repr2>"

def test_user_auth0_subject_required(db):
    """Test that auth0_subject is required (nullable=False)."""
    with pytest.raises(IntegrityError):
        user = User(email="no_auth0@example.com") # auth0_subject is None
        db.session.add(user)
        db.session.commit()
    db.session.rollback() # Important after an IntegrityError

def test_user_auth0_subject_unique(db):
    """Test that auth0_subject must be unique."""
    auth0_id = "auth0|unique_subject"
    user1 = User(auth0_subject=auth0_id, email="user1@example.com")
    db.session.add(user1)
    db.session.commit()

    with pytest.raises(IntegrityError):
        user2 = User(auth0_subject=auth0_id, email="user2@example.com")
        db.session.add(user2)
        db.session.commit()
    db.session.rollback()

def test_user_email_unique(db):
    """Test that email must be unique (if provided)."""
    email_addr = "unique_email@example.com"
    user1 = User(auth0_subject="auth0|user_for_email1", email=email_addr)
    db.session.add(user1)
    db.session.commit()

    with pytest.raises(IntegrityError):
        user2 = User(auth0_subject="auth0|user_for_email2", email=email_addr)
        db.session.add(user2)
        db.session.commit()
    db.session.rollback()

def test_user_email_can_be_null(db):
    """Test that email can be null."""
    user = User(auth0_subject="auth0|null_email_user")
    db.session.add(user)
    db.session.commit()
    assert user.id is not None
    assert user.email is None

def test_user_expenses_relationship_cascade_delete(db):
    """Test that deleting a User cascades to delete their Expenses."""
    user = User(auth0_subject="auth0|user_with_expenses")
    db.session.add(user)
    db.session.commit() # Commit user to get an ID

    expense1 = Expense(user_id=user.id, description="Laptop", amount=1200.00)
    expense2 = Expense(user_id=user.id, description="Coffee", amount=5.00)
    db.session.add_all([expense1, expense2])
    db.session.commit()

    assert len(user.expenses) == 2
    assert Expense.query.count() == 2

    user_id_to_delete = user.id
    db.session.delete(user)
    db.session.commit()

    assert db.session.get(User, user_id_to_delete) is None
    assert Expense.query.filter_by(user_id=user_id_to_delete).count() == 0
    assert Expense.query.count() == 0 # All expenses should be gone