from sqlalchemy.orm import validates

from extensions import db, bcrypt

VALID_ROLES = ("employee", "manager")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    _password_hash = db.Column("password_hash", db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="employee")

    # Historical orders/adjustments intentionally are NOT cascade-deleted with
    # the user -- an account being removed should never erase sales history.
    orders = db.relationship("Order", back_populates="created_by_user")
    queue_adjustments = db.relationship("QueueAdjustment", back_populates="applied_by_user")
    inventory_receipts = db.relationship("InventoryReceipt", back_populates="logged_by_user")

    @property
    def password_hash(self):
        raise AttributeError("password_hash is write-only")

    @password_hash.setter
    def password_hash(self, plaintext_password):
        self._password_hash = bcrypt.generate_password_hash(plaintext_password).decode("utf-8")

    def authenticate(self, plaintext_password):
        return bcrypt.check_password_hash(self._password_hash, plaintext_password)

    @validates("role")
    def validate_role(self, key, value):
        if value not in VALID_ROLES:
            raise ValueError(f"role must be one of {VALID_ROLES}")
        return value

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
