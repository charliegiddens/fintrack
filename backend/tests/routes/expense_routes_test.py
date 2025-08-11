import pytest
import datetime
from datetime import timezone
from decimal import Decimal

@pytest.mark.usefixtures("seed_test_user")
def test_create_expense_success(client, db):
    data = {
        "description": "Lunch",
        "amount": "12.34",
        "category": "Food",
        "date": datetime.datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }
    response = client.post("/create", json=data)
    assert response.status_code == 201
    response_data = response.get_json()
    assert response_data["description"] == data["description"]
    assert response_data["amount"] == str(Decimal(data["amount"]))

@pytest.mark.usefixtures("seed_test_user")
def test_create_expense_missing_fields(client):
    data = {
        "fake_field": "fake_data"
    }
    response = client.post("/create", json=data)
    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data == {"error": "Missing required fields: description, amount"}

@pytest.mark.usefixtures("seed_test_user")
def test_create_expense_invalid_amount(client):
    data = {"description": "Dinner", "amount": "invalid"}
    response = client.post("/create", json=data)
    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data == {"error": "Invalid amount format. Must be a number."}

@pytest.mark.usefixtures("seed_test_user")
def test_create_expense_negative_amount(client):
    data = {"description": "Refund", "amount": "-10.00"}
    response = client.post("/create", json=data)
    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data == {"error": "Amount must be a positive number."}

@pytest.mark.usefixtures("seed_test_user")
def test_create_expense_invalid_description(client):
    data = {"description": "", "amount": "5.00"}
    response = client.post("/create", json=data)
    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data == {"error": "Description must be a string between 1 and 200 characters."}

@pytest.mark.usefixtures("seed_test_user")
def test_create_expense_invalid_date_format(client):
    data = {
        "description": "Groceries",
        "amount": "25.00",
        "date": "not-a-date"
    }
    response = client.post("/create", json=data)
    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data == {"error": "Invalid date format. Please use ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SSZ)."}

@pytest.mark.usefixtures("seed_test_user")
def test_create_expense_invalid_category(client):
    data = {
        "description": "Dinner",
        "amount": "15.00",
        "category": "X" * 51
    }
    response = client.post("/create", json=data)
    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data == {"error": "Category, if provided, must be a string no longer than 50 characters."}

@pytest.mark.usefixtures("seed_test_user")
def test_create_expense_user_not_found(client, mocker):
    mocker.patch("routes.expense_routes.get_or_create_internal_user_id", return_value=None)
    
    response = client.post('/create', json={
        "description": "Test expense",
        "amount": 100.0
    })

    assert response.status_code == 404
    response_data = response.get_json()
    assert response_data == {"error": "Authenticated user not found in local database."}


@pytest.mark.usefixtures("seed_test_user")
def test_create_expense_db_failure(client, mocker):
    mocker.patch("app.extensions.db.session.commit", side_effect=Exception("DB error"))
    data = {"description": "Taxi", "amount": "20.00"}
    response = client.post("/create", json=data)
    assert response.status_code == 500
    response_data = response.get_json()
    # referencing specific "error" json index because the expense_routes logic also prints the DB error itself
    assert response_data["error"] == "An error occurred while creating the expense."

@pytest.mark.usefixtures("seed_test_user")
def test_get_expense_by_id_success(client, db):
    from models.expense import Expense
    expense = Expense(
        user_id=1,
        description="Test Expense",
        amount=Decimal("10.00"),
        category="Transport",
        date=datetime.datetime.now(timezone.utc)
    )
    db.session.add(expense)
    db.session.commit()
    response = client.get(f"/get_by_id/{expense.id}")
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data["description"] == expense.description

@pytest.mark.usefixtures("seed_test_user")
def test_get_expense_by_id_not_found(client):
    response = client.get("/get_by_id/9999")
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data == []

@pytest.mark.usefixtures("seed_test_user")
def test_get_expense_by_id_wrong_user(client, mocker, db, seed_test_user):

    from models.user import User
    another_user = User(id=2, auth0_subject="auth0|anotheruser", email="another@example.com")
    db.session.add(another_user)
    db.session.commit()

    from models.expense import Expense
    expense = Expense(
        user_id=another_user.id,
        description="Test Expense",
        amount=Decimal("10.00"),
        category="Transport",
        date=datetime.datetime.now(timezone.utc)
    )
    db.session.add(expense)
    db.session.commit()

    mocker.patch('routes.expense_routes.get_or_create_internal_user_id', return_value=1)

    response = client.get(f"/get_by_id/{expense.id}")
    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data == []

@pytest.mark.usefixtures("seed_test_user")
def test_get_expense_user_not_found(client, mocker):
    mocker.patch("routes.expense_routes.get_or_create_internal_user_id", return_value=None)
    response = client.get("/get_by_id/1")
    assert response.status_code == 404
    response_data = response.get_json()
    assert response_data == {"error": "Authenticated user not found in local database."}
