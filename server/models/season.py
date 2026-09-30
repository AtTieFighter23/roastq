import datetime

from extensions import db


class Season(db.Model):
    __tablename__ = "seasons"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False, unique=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    orders = db.relationship("Order", back_populates="season")

    @staticmethod
    def default_dates_for_year(year):
        """Company default season window: Aug 1 - Oct 1, editable by a manager."""
        return datetime.date(year, 8, 1), datetime.date(year, 10, 1)

    def __repr__(self):
        return f"<Season {self.year}: {self.start_date} to {self.end_date}>"
