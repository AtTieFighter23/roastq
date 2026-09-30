from datetime import datetime, timezone

from sqlalchemy.orm import validates

from extensions import db

VALID_TYPES = ("delay_minutes", "mark_finished_early", "throughput_mode", "reorder", "note")


class QueueAdjustment(db.Model):
    __tablename__ = "queue_adjustments"

    id = db.Column(db.Integer, primary_key=True)
    # Nullable because a throughput_mode change applies globally, not to one order.
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=True)
    type = db.Column(db.String(30), nullable=False)
    value = db.Column(db.String(255), nullable=True)
    applied_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    order = db.relationship("Order", back_populates="queue_adjustments")
    applied_by_user = db.relationship("User", back_populates="queue_adjustments")

    @validates("type")
    def validate_type(self, key, value):
        if value not in VALID_TYPES:
            raise ValueError(f"type must be one of {VALID_TYPES}")
        return value

    def __repr__(self):
        return f"<QueueAdjustment {self.type}={self.value}>"
