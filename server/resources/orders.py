from datetime import datetime

from flask import request, session
from flask_restful import Resource

from extensions import db
from models.order import Order
from models.sack_item import SackItem
from models.season import Season
from schemas import order_schema, orders_schema, sack_item_schema
from decorators import login_required


class Orders(Resource):
    @login_required
    def get(self):
        business_date = request.args.get("business_date")
        query = Order.query
        if business_date:
            query = query.filter_by(business_date=datetime.strptime(business_date, "%Y-%m-%d").date())
        return orders_schema.dump(query.order_by(Order.created_at).all()), 200

    @login_required
    def post(self):
        """Creates an Order, optionally with an initial list of sack_items in
        the same request. display_number is computed server-side and resets
        each business_date -- never accepted from the client.
        """
        data = request.get_json() or {}
        today = datetime.utcnow().date()

        season = Season.query.filter(Season.start_date <= today, Season.end_date >= today).first()
        if not season:
            return {"error": "No active season is configured for today's date."}, 422

        for item in data.get("sack_items", []):
            errors = sack_item_schema.validate(item)
            if errors:
                return {"error": errors}, 422

        try:
            order = Order(
                display_number=Order.next_display_number_for(today),
                business_date=today,
                customer_name=data.get("customer_name"),
                contact_info=data.get("contact_info"),
                created_by=session["user_id"],
                season_id=season.id,
            )
            db.session.add(order)
            db.session.flush()  # assigns order.id before we attach sack items

            next_seq = (db.session.query(db.func.max(SackItem.queue_sequence)).scalar() or 0)
            for item in data.get("sack_items", []):
                next_seq += 1
                db.session.add(SackItem(
                    order_id=order.id,
                    queue_sequence=next_seq,
                    size=item["size"],
                    service=item["service"],
                    color_stage=item["color_stage"],
                    variety_1=item["variety_1"],
                    variety_2=item.get("variety_2"),
                    addon_note=item.get("addon_note"),
                ))

            db.session.commit()
            return order_schema.dump(order), 201
        except (KeyError, ValueError) as e:
            db.session.rollback()
            return {"error": str(e)}, 422


class OrderByID(Resource):
    @login_required
    def get(self, id):
        order = Order.query.get_or_404(id)
        return order_schema.dump(order), 200

    @login_required
    def patch(self, id):
        order = Order.query.get_or_404(id)
        data = request.get_json() or {}
        try:
            for attr in ("customer_name", "contact_info", "status", "manager_note"):
                if attr in data:
                    setattr(order, attr, data[attr])
            db.session.commit()
            return order_schema.dump(order), 200
        except ValueError as e:
            db.session.rollback()
            return {"error": str(e)}, 422

    @login_required
    def delete(self, id):
        order = Order.query.get_or_404(id)
        db.session.delete(order)
        db.session.commit()
        return {}, 204
