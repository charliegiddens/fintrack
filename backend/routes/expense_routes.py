from flask import Blueprint, jsonify, g, request
from app.auth_utils import requires_auth
from models.expense import Expense
from app.api_helpers import get_or_create_internal_user_id
from decimal import Decimal
import datetime
from datetime import timezone
from app.extensions import db

expense_bp = Blueprint('expenses', __name__)

@expense_bp.route("/create", methods=['POST'])
@requires_auth
def create_expense():
    auth0_subject_id = g.current_user.get("sub")
    email = g.current_user.get("email")
    fintrack_user_id = get_or_create_internal_user_id(
        auth0_subject_id,
        email=email,
        create_if_missing=True
    )

    if not fintrack_user_id:
        return jsonify({"error": "Authenticated user not found in local database."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # --- Data Validation ---
    required_fields = ['description', 'amount']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    description = data.get('description')
    amount_str = data.get('amount')
    category = data.get('category')  # Optional
    date_str = data.get('date')     # Optional, defaults to now if not provided
    
    try:
        amount = Decimal(str(amount_str))
        if amount <= 0:  # Assuming expenses must be positive
            return jsonify({"error": "Amount must be a positive number."}), 400
    except Exception:
        return jsonify({"error": "Invalid amount format. Must be a number."}), 400

    if not isinstance(description, str) or not (0 < len(description) <= 200):
        return jsonify({"error": "Description must be a string between 1 and 200 characters."}), 400

    expense_date = datetime.datetime.now(timezone.utc)  # Default to now
    if date_str:
        try:
            expense_date = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid date format. Please use ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SSZ)."}), 400

    if category and (not isinstance(category, str) or len(category) > 50):
        return jsonify({"error": "Category, if provided, must be a string no longer than 50 characters."}), 400

    # --- Create Expense ---
    try:
        new_expense = Expense(
            user_id=fintrack_user_id,
            date=expense_date,
            description=description,
            amount=amount,
            category=category
        )
        db.session.add(new_expense)
        db.session.commit()
        return jsonify(new_expense.to_dict()), 201  # 201 Created
    except Exception as e:
        db.session.rollback()
        print(f"Error creating expense: {e}")  # Basic logging
        return jsonify({"error": "An error occurred while creating the expense."}), 500


@expense_bp.route("/get_by_id/<int:expense_id>", methods=['GET'])
@requires_auth
def get_expense_by_id(expense_id): # expense_id is now a path parameter
    auth0_subject_id = g.current_user.get("sub")
    fintrack_user_id = get_or_create_internal_user_id(auth0_subject_id)

    if not fintrack_user_id:
        return jsonify({"error": "Authenticated user not found in local database."}), 404

    # --- Query for the specific expense belonging to the user ---
    # We filter by both expense_id AND user_id for security.
    expense = Expense.query.filter_by(id=expense_id).first()

    if expense:
        if ( expense.to_dict()["user_id"] == fintrack_user_id ):
            return jsonify(expense.to_dict()), 200
        else:
            return jsonify({"error": "Access denied."}), 401
    elif not expense:
        return jsonify({"error": "Expense not found."}), 404
