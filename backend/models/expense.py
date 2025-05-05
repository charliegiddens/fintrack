import datetime
from extensions import db # Import the shared db instance

# Rename class from Transaction to Expense
class Expense(db.Model):
    # Rename table from 'transactions' to 'expenses'
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    # Foreign key linking to the 'id' column of the 'users' table (no change needed here)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow, index=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(50), nullable=True)

    # Note: The 'user' attribute (for Expense -> User access)
    # is automatically created by the backref in the User model.

    # Update __repr__ to reflect the new class name
    def __repr__(self):
        return f'<Expense {self.id} - {self.description} ({self.amount})>'