from datetime import datetime, timezone

from flask import request, session
from flask_restful import Resource

from extensions import db
from models.order import Order
from models.sack_item import SackItem
from models.queue_adjustment import QueueAdjustment
from schemas import sack_item_schema
from decorators import login_required


class OrderSackItems(Resource):
    @login_required
    def post(self, order_id):
        order = Order.query.get_or_404(order_id)
        data = request.get_json() or {}

        errors = sack_item_schema.validate(data)
        if errors:
            return {"error": errors}, 422

        next_seq = (db.session.query(db.func.max(SackItem.queue_sequence)).scalar() or 0) + 1
        try:
            sack = SackItem(
                order_id=order.id,
                queue_sequence=next_seq,
                size=data["size"],
                service=data["service"],
                color_stage=data["color_stage"],
                variety_1=data["variety_1"],
                variety_2=data.get("variety_2"),
                addon_note=data.get("addon_note"),
            )
            db.session.add(sack)
            db.session.commit()
            return sack_item_schema.dump(sack), 201
        except ValueError as e:
            db.session.rollback()
            return {"error": str(e)}, 422


class SackItemByID(Resource):
    @login_required
    def patch(self, id):
        """Handles both routine status updates and the employee's
        'mark finished early' action in one endpoint.
        """
        sack = SackItem.query.get_or_404(id)
        data = request.get_json() or {}

        try:
            if data.get("mark_finished"):
                sack.sack_status = "done"
                sack.actual_finish_at = datetime.now(timezone.utc)
                db.session.add(QueueAdjustment(
                    order_id=sack.order_id,
                    type="mark_finished_early",
                    value=f"sack_id={sack.id}",
                    applied_by=session["user_id"],
                ))
            elif "sack_status" in data:
                sack.sack_status = data["sack_status"]

            db.session.commit()
            return sack_item_schema.dump(sack), 200
        except ValueError as e:
            db.session.rollback()
            return {"error": str(e)}, 422

    @login_required
    def delete(self, id):
        sack = SackItem.query.get_or_404(id)
        db.session.delete(sack)
        db.session.commit()
        return {}, 204
