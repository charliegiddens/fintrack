import datetime
from datetime import timezone
from app.extensions import db

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    # using datetime now as a fallback for unentered date. Think about frontend validation for this
    date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.datetime.now(timezone.utc), index=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.datetime.now(timezone.utc), index=True)

    def to_dict(self):
        """Helper method to convert model instance to dictionary"""

        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'description': self.description,
            'amount': self.amount,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.date else None
        }

    def __repr__(self):
        return f'<Expense {self.id} - {self.description} ({self.amount})>'