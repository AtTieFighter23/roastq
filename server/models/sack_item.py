from sqlalchemy.orm import validates

from extensions import db

VALID_SIZES = ("sack", "half_sack")
VALID_SERVICES = ("fresh", "roast_only", "cooled")
VALID_COLOR_STAGES = ("green", "red")
VALID_VARIETIES = ("NM64", "BigJim", "Sandia", "DoubleCross", "Lumbre")
VALID_SACK_STATUSES = ("queued", "roasting", "peeling", "done")


class SackItem(db.Model):
    __tablename__ = "sack_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)

    size = db.Column(db.String(10), nullable=False)
    service = db.Column(db.String(15), nullable=False)
    color_stage = db.Column(db.String(5), nullable=False)
    variety_1 = db.Column(db.String(20), nullable=False)
    variety_2 = db.Column(db.String(20), nullable=True)
    addon_note = db.Column(db.String(255), nullable=True)  # free-text jalapeno/guerito add-ins

    queue_sequence = db.Column(db.Integer, nullable=True)
    sack_status = db.Column(db.String(10), nullable=False, default="queued")
    estimated_finish_at = db.Column(db.DateTime, nullable=True)
    actual_finish_at = db.Column(db.DateTime, nullable=True)

    order = db.relationship("Order", back_populates="sack_items")

    # NOTE: these column-level validators are a basic guard. Because
    # SQLAlchemy validates attributes one at a time as they're assigned, the
    # order fields are set in matters (e.g. setting variety_2 before size is
    # known). The AUTHORITATIVE cross-field check (half-sacks can't mix,
    # variety_2 != variety_1) lives in schemas.py, where the whole payload is
    # validated together before anything touches the database.

    @validates("size")
    def validate_size(self, key, value):
        if value not in VALID_SIZES:
            raise ValueError(f"size must be one of {VALID_SIZES}")
        return value

    @validates("service")
    def validate_service(self, key, value):
        if value not in VALID_SERVICES:
            raise ValueError(f"service must be one of {VALID_SERVICES}")
        return value

    @validates("color_stage")
    def validate_color_stage(self, key, value):
        if value not in VALID_COLOR_STAGES:
            raise ValueError(f"color_stage must be one of {VALID_COLOR_STAGES}")
        return value

    @validates("variety_1")
    def validate_variety_1(self, key, value):
        if value not in VALID_VARIETIES:
            raise ValueError(f"variety_1 must be one of {VALID_VARIETIES}")
        return value

    @validates("variety_2")
    def validate_variety_2(self, key, value):
        if value is None:
            return value
        if value not in VALID_VARIETIES:
            raise ValueError(f"variety_2 must be one of {VALID_VARIETIES}")
        return value

    @validates("sack_status")
    def validate_sack_status(self, key, value):
        if value not in VALID_SACK_STATUSES:
            raise ValueError(f"sack_status must be one of {VALID_SACK_STATUSES}")
        return value

    def __repr__(self):
        return f"<SackItem {self.size} {self.service} {self.variety_1}/{self.variety_2 or '-'}>"
