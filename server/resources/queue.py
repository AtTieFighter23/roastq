from flask import request, session
from flask_restful import Resource

from extensions import db
from models.order import Order
from models.queue_adjustment import QueueAdjustment
from decorators import login_required, manager_required
from services.queue_service import compute_public_queue, reorder_queue


class PublicQueue(Resource):
    """No authentication required -- this is the whole point of the app for
    customers. Never returns customer_name or any other personal info.
    """
    def get(self):
        return compute_public_queue(), 200


class QueueDelay(Resource):
    """Either an employee or a manager can add flat delay minutes (e.g. a
    spill that needs cleaning up) -- this does not require manager rank.
    """
    @login_required
    def post(self):
        data = request.get_json() or {}
        try:
            minutes = int(data.get("minutes"))
        except (TypeError, ValueError):
            return {"error": "minutes must be an integer."}, 422

        db.session.add(QueueAdjustment(
            type="delay_minutes",
            value=str(minutes),
            applied_by=session["user_id"],
            order_id=data.get("order_id"),
        ))
        db.session.commit()
        return {"message": f"Added {minutes} minute(s) to the queue."}, 201


class QueueThroughputMode(Resource):
    """Manager-only: only a manager can declare the line normal/degraded/halted."""
    @manager_required
    def post(self):
        data = request.get_json() or {}
        mode = data.get("mode")
        if mode not in ("normal", "degraded", "halted"):
            return {"error": "mode must be 'normal', 'degraded', or 'halted'."}, 422

        db.session.add(QueueAdjustment(type="throughput_mode", value=mode, applied_by=session["user_id"]))
        db.session.commit()
        return {"message": f"Throughput mode set to {mode}."}, 201


class QueueReorder(Resource):
    """Manager-only: move a priority order (e.g. a replacement) ahead in line."""
    @manager_required
    def post(self):
        data = request.get_json() or {}
        try:
            reorder_queue(
                moving_order_id=data["moving_order_id"],
                after_order_id=data.get("after_order_id"),
                applied_by_user_id=session["user_id"],
            )
            return {"message": "Queue reordered."}, 200
        except (KeyError, ValueError) as e:
            db.session.rollback()
            return {"error": str(e)}, 422


class QueueNote(Resource):
    """Either role can leave a customer-visible note on an order."""
    @login_required
    def post(self):
        data = request.get_json() or {}
        order = Order.query.get_or_404(data.get("order_id"))
        order.manager_note = data.get("note", "")
        db.session.commit()
        return {"message": "Note updated."}, 200
