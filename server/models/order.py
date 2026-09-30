from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import validates

from extensions import db

VALID_STATUSES = ("queued", "in_progress", "finished", "picked_up")


class Order(db.Model):
    __tablename__ = "orders"
    __table_args__ = (
        # display_number resets to 1 each business day -- it is only unique
        # *within* a given day, never globally. The auto-incrementing `id`
        # above is the permanent, never-reused identifier used by every
        # foreign key and every historical/analytics query.
        UniqueConstraint("display_number", "business_date", name="uq_order_display_per_day"),
    )

    id = db.Column(db.Integer, primary_key=True)
    display_number = db.Column(db.Integer, nullable=False)
    business_date = db.Column(db.Date, nullable=False)
    customer_name = db.Column(db.String(100), nullable=True)  # never exposed on the public queue
    contact_info = db.Column(db.String(120), nullable=True)  # reserved for future email/SMS notification
    status = db.Column(db.String(20), nullable=False, default="queued")
    manager_note = db.Column(db.String(255), nullable=True)  # customer-visible note
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey("seasons.id"), nullable=False)

    created_by_user = db.relationship("User", back_populates="orders")
    season = db.relationship("Season", back_populates="orders")
    sack_items = db.relationship(
        "SackItem", back_populates="order", cascade="all, delete-orphan", order_by="SackItem.queue_sequence"
    )
    queue_adjustments = db.relationship(
        "QueueAdjustment", back_populates="order", cascade="all, delete-orphan"
    )

    @validates("status")
    def validate_status(self, key, value):
        if value not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}")
        return value

    @staticmethod
    def next_display_number_for(business_date):
        last = (
            db.session.query(db.func.max(Order.display_number))
            .filter(Order.business_date == business_date)
            .scalar()
        )
        return (last or 0) + 1

    def __repr__(self):
        return f"<Order #{self.display_number} on {self.business_date}>"
