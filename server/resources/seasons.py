from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from models.season import Season
from schemas import season_schema, seasons_schema
from decorators import manager_required


class Seasons(Resource):
    @manager_required
    def get(self):
        return seasons_schema.dump(Season.query.order_by(Season.year.desc()).all()), 200

    @manager_required
    def post(self):
        json_data = request.get_json() or {}

        if "year" not in json_data:
            return {"error": "year is required."}, 422

        # Fall back to the company default (Aug 1 - Oct 1) for any date the
        # manager doesn't explicitly override.
        default_start, default_end = Season.default_dates_for_year(json_data["year"])
        json_data.setdefault("start_date", default_start.isoformat())
        json_data.setdefault("end_date", default_end.isoformat())

        try:
            # .load() is what actually parses "2026-08-01" into a real
            # datetime.date -- reading request.get_json() directly and
            # assigning the raw string to the model would crash at commit
            # time, since SQLite's Date adapter calls .isoformat() on the
            # value, which a plain string doesn't have.
            validated = season_schema.load(json_data)
        except ValidationError as err:
            return {"error": err.messages}, 422

        season = Season(**validated)
        db.session.add(season)
        db.session.commit()
        return season_schema.dump(season), 201


class SeasonByID(Resource):
    @manager_required
    def patch(self, id):
        season = Season.query.get_or_404(id)
        json_data = request.get_json() or {}

        try:
            validated = season_schema.load(json_data, partial=True)
        except ValidationError as err:
            return {"error": err.messages}, 422

        for attr, value in validated.items():
            setattr(season, attr, value)

        db.session.commit()
        return season_schema.dump(season), 200
