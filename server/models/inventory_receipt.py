from datetime import date as date_cls

from sqlalchemy.orm import validates

from extensions import db

# Includes the two off-menu, sold-by-pound varieties since managers still need
# to log when those are received, even though they rarely go through roasting.
VALID_INVENTORY_VARIETIES = ("NM64", "BigJim", "Sandia", "DoubleCross", "Lumbre", "Jalapeno", "Guerito")
VALID_COLOR_STAGES = ("green", "red")


class InventoryReceipt(db.Model):
    __tablename__ = "inventory_receipts"

    id = db.Column(db.Integer, primary_key=True)
    variety = db.Column(db.String(20), nullable=False)
    color_stage = db.Column(db.String(5), nullable=False)
    sacks_received = db.Column(db.Float, nullable=False)  # tracked by the sack, not by weight
    date_received = db.Column(db.Date, nullable=False, default=date_cls.today)
    sold_out = db.Column(db.Boolean, nullable=False, default=False)  # manually toggled by a manager

    logged_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    logged_by_user = db.relationship("User", back_populates="inventory_receipts")

    @validates("variety")
    def validate_variety(self, key, value):
        if value not in VALID_INVENTORY_VARIETIES:
            raise ValueError(f"variety must be one of {VALID_INVENTORY_VARIETIES}")
        return value

    @validates("color_stage")
    def validate_color_stage(self, key, value):
        if value not in VALID_COLOR_STAGES:
            raise ValueError(f"color_stage must be one of {VALID_COLOR_STAGES}")
        return value

    def __repr__(self):
        return f"<InventoryReceipt {self.sacks_received} sacks {self.variety}/{self.color_stage}>"
