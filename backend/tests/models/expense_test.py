import pytest
from sqlalchemy.exc import IntegrityError
import datetime
from datetime import timezone
from decimal import Decimal

from models.user import User
from models.expense import Expense

@pytest.fixture
def sample_user(db):
    """Fixture to create a sample user for expense tests."""
    user = User(auth0_subject="auth0|expense_user", email="expense_user@example.com")
    db.session.add(user)
    db.session.commit()
    return user

def test_create_expense(db, sample_user):
    """Test creating a new Expense instance."""

    created_at_time = datetime.datetime.now(timezone.utc).replace(microsecond=0)
    expense_data = {
        "user_id": sample_user.id,
        "description": "Groceries",
        "amount": Decimal("75.50"), # Decimal for Numeric fields
        "category": "Food",
        "created_at": created_at_time

    }
    expense = Expense(**expense_data)
    db.session.add(expense)
    db.session.commit()

    assert expense.id is not None
    assert expense.user_id == sample_user.id
    assert expense.description == "Groceries"
    assert expense.amount == Decimal("75.50")
    assert expense.category == "Food"
    assert expense.date is not None # Should have default date
    assert expense.created_at is not None # Should have default date
    assert isinstance(expense.date, datetime.datetime)
    assert isinstance(expense.created_at, datetime.datetime)

def test_expense_repr(db, sample_user):
    """Test the __repr__ method of Expense."""
    expense = Expense(
        user_id=sample_user.id,
        description="Dinner",
        amount=Decimal("25.00")
    )
    db.session.add(expense)
    db.session.commit() # Need ID for repr
    expected_repr = f"<Expense {expense.id} - Dinner (25.00)>"
    assert repr(expense) == expected_repr

def test_expense_to_dict(db, sample_user):
    """Test the to_dict method of Expense."""
    # It's an aware datetime object.
    aware_insert_time = datetime.datetime.now(timezone.utc).replace(microsecond=0)

    expense_to_insert = Expense(
        user_id=sample_user.id,
        date=aware_insert_time, # Insert aware datetime
        description="Software Subscription",
        amount=Decimal("19.99"),
        category="Software",
        created_at=aware_insert_time
    )
    db.session.add(expense_to_insert)
    db.session.commit()

    retrieved_expense = db.session.get(Expense, expense_to_insert.id) # naive
    actual_dict = retrieved_expense.to_dict()
    expected_naive_iso_date_string = retrieved_expense.date.isoformat()

    expected_dict = {
        'id': retrieved_expense.id,
        'user_id': retrieved_expense.user_id, 
        'date': expected_naive_iso_date_string,
        'description': "Software Subscription",
        'amount': Decimal("19.99"),
        'category': "Software",
        'created_at': expected_naive_iso_date_string
    }

    assert actual_dict == expected_dict



def test_expense_default_date(db, sample_user):
    """Test that the date field gets a default UTC datetime."""
    expense = Expense(
        user_id=sample_user.id,
        description="Item with default date",
        amount=Decimal("1.00")
    )
    db.session.add(expense)
    db.session.commit() # executes the lambda for now() calculation

    retrieved_expense = db.session.get(Expense, expense.id)
    expense_date_from_db = retrieved_expense.date

    assert expense_date_from_db is not None
    assert isinstance(expense_date_from_db, datetime.datetime)

    # Make the naive datetime from DB aware of its UTC nature
    if expense_date_from_db.tzinfo is None:
        expense_date_from_db = expense_date_from_db.replace(tzinfo=timezone.utc)

    current_utc_time = datetime.datetime.now(timezone.utc)
    time_difference_seconds = (current_utc_time - expense_date_from_db).total_seconds()

    assert abs(time_difference_seconds) < 5 # Use abs() in case of slight clock differences

def test_expense_missing_description_raises_integrity_error(db, sample_user):
    """Test IntegrityError for missing description (nullable=False)."""
    with pytest.raises(IntegrityError, match="description"): # Optional: match specific error message part
        expense = Expense(user_id=sample_user.id, amount=Decimal("10.00")) # description is None
        # print(f"Expense before commit (missing desc): {vars(expense)}") # Debug print
        db.session.add(expense)
        db.session.commit()
    db.session.rollback()

def test_expense_missing_amount_raises_integrity_error(db, sample_user):
    """Test IntegrityError for missing amount (nullable=False)."""
    with pytest.raises(IntegrityError, match="amount"): # Optional: match specific error message part
        expense = Expense(user_id=sample_user.id, description="Missing amount") # amount is None
        # print(f"Expense before commit (missing amount): {vars(expense)}") # Debug print
        db.session.add(expense)
        db.session.commit()
    db.session.rollback()

def test_expense_missing_user_id_raises_integrity_error(db): # sample_user not strictly needed here
    """Test IntegrityError for missing user_id (nullable=False)."""
    with pytest.raises(IntegrityError, match="user_id"): # Optional: match specific error message part
        expense = Expense(description="No user", amount=Decimal("5.00")) # user_id is None
        # print(f"Expense before commit (missing user_id): {vars(expense)}") # Debug print
        db.session.add(expense)
        db.session.commit()
    db.session.rollback()

def test_expense_invalid_foreign_key_user_id_raises_integrity_error(db):
    """Test IntegrityError for non-existent user_id (FOREIGN KEY constraint)."""
    # This match might be more specific to FOREIGN KEY in some DBs
    with pytest.raises(IntegrityError, match=r"(FOREIGN KEY|foreign key|violates foreign key constraint)"):
        expense = Expense(user_id=99999, # Non-existent user ID
                          description="Orphan expense",
                          amount=Decimal("5.00"))
        # print(f"Expense before commit (invalid FK user_id): {vars(expense)}") # Debug print
        db.session.add(expense)
        db.session.commit()
    db.session.rollback()
