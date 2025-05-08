# import pytest
# import json
# from decimal import Decimal
# import datetime
# from datetime import timezone

# from models.expense import Expense
# from models.user import User

# from ..conftest import MOCK_FINTRACK_USER_ID, MOCK_AUTH0_SUBJECT_ID

# --- Tests for POST /expenses/create ---

# def test_create_expense_success(client, db, seed_test_user):
#     """Test successful expense creation."""

#     expense_data = Expense(
#         "description": "Lunch with client",
#         "amount": Decimal(str("25.50")),
#         "category": "Meals",
#         "date": datetime.datetime.now(timezone.utc).isoformat()
#     )

#     response = client.post('/api/expenses/create', json=expense_data)

#     assert response.status_code == 201
#     data = response.get_json()
#     assert data["description"] == expense_data["description"]
#     assert Decimal(str(data["amount"])) == Decimal(expense_data["amount"]) # Compare as Decimal
#     assert data["category"] == expense_data["category"]
#     assert data["user_id"] == MOCK_FINTRACK_USER_ID

#     # Verify in DB
#     created_expense = db.session.get(Expense, data["id"])
#     assert created_expense is not None
#     assert created_expense.user_id == MOCK_FINTRACK_USER_ID

# def test_create_expense_no_fintrack_user(client, mock_get_internal_user_id):
#     """Test expense creation when fintrack_user_id is not found (mocked)."""
#     mock_get_internal_user_id.return_value = None # Override default mock

#     expense_data = {"description": "Test", "amount": "10"}
#     response = client.post('/expenses/create', json=expense_data)

#     assert response.status_code == 404
#     data = response.get_json()
#     assert "Authenticated user not found" in data["error"]

# def test_create_expense_missing_fields(client, seed_test_user):
#     """Test request with missing required fields."""
#     expense_data = {"description": "Only description"} # Missing amount
#     response = client.post('/expenses/create', json=expense_data)

#     assert response.status_code == 400
#     data = response.get_json()
#     assert "Missing required fields: amount" in data["error"]

# def test_create_expense_invalid_amount_format(client, seed_test_user):
#     expense_data = {"description": "Test", "amount": "not-a-number"}
#     response = client.post('/expenses/create', json=expense_data)
#     assert response.status_code == 400
#     data = response.get_json()
#     assert "Invalid amount format" in data["error"]

# def test_create_expense_negative_amount(client, seed_test_user):
#     expense_data = {"description": "Test", "amount": "-5.00"}
#     response = client.post('/expenses/create', json=expense_data)
#     assert response.status_code == 400
#     data = response.get_json()
#     assert "Amount must be a positive number" in data["error"]

# def test_create_expense_invalid_date_format(client, seed_test_user):
#     expense_data = {
#         "description": "Invalid date test",
#         "amount": "10.00",
#         "date": "2023-13-01T00:00:00Z" # Invalid month
#     }
#     response = client.post('/expenses/create', json=expense_data)
#     assert response.status_code == 400
#     data = response.get_json()
#     assert "Invalid date format" in data["error"]

# # --- Tests for GET /expenses/get_by_id/<int:expense_id> ---

# def test_get_expense_by_id_success(client, db, seed_test_user):
#     """Test successfully getting an expense by its ID."""
#     expense_date = datetime.datetime.now(timezone.utc)
#     expense = Expense(
#         user_id=MOCK_FINTRACK_USER_ID,
#         date=expense_date,
#         description="Test Expense to Get",
#         amount=Decimal("99.99"),
#         category="Testing"
#     )
#     db.session.add(expense)
#     db.session.commit()

#     response = client.get(f'/expenses/get_by_id/{expense.id}')

#     assert response.status_code == 200
#     data = response.get_json()
#     assert data["id"] == expense.id
#     assert data["description"] == "Test Expense to Get"
#     assert data["user_id"] == MOCK_FINTRACK_USER_ID

# def test_get_expense_by_id_not_found(client):
#     """Test getting an expense that doesn't exist."""
#     response = client.get('/expenses/get_by_id/99999')
#     assert response.status_code == 404
#     data = response.get_json()
#     assert "Expense not found or access denied" in data["error"]

# def test_get_expense_by_id_belongs_to_other_user(client, db):
#     """Test trying to get an expense that belongs to another user."""
#     other_user = User(id=MOCK_FINTRACK_USER_ID + 1, auth0_subject="auth0|otheruser", email="other@example.com")
#     db.session.add(other_user)
#     db.session.commit()

#     other_expense = Expense(
#         user_id=other_user.id,
#         date=datetime.datetime.now(timezone.utc),
#         description="Other User's Expense",
#         amount=Decimal("50.00")
#     )
#     db.session.add(other_expense)
#     db.session.commit()

#     response = client.get(f'/expenses/get_by_id/{other_expense.id}')

#     assert response.status_code == 404
#     data = response.get_json()
#     assert "Expense not found or access denied" in data["error"]

# def test_get_expense_by_id_no_fintrack_user(client, mock_get_internal_user_id):
#     """Test getting an expense when the authenticated user has no local Fintrack ID."""
#     mock_get_internal_user_id.return_value = None

#     response = client.get('/expenses/get_by_id/1')
#     assert response.status_code == 404
#     data = response.get_json()
#     assert "Authenticated user not found" in data["error"]
