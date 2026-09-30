from flask import request, session
from flask_restful import Resource

from extensions import db
from models.inventory_receipt import InventoryReceipt
from schemas import inventory_receipt_schema, inventory_receipts_schema
from decorators import manager_required


class InventoryReceipts(Resource):
    @manager_required
    def get(self):
        receipts = InventoryReceipt.query.order_by(InventoryReceipt.date_received.desc()).all()
        return inventory_receipts_schema.dump(receipts), 200

    @manager_required
    def post(self):
        data = request.get_json() or {}
        try:
            receipt = InventoryReceipt(
                variety=data["variety"],
                color_stage=data["color_stage"],
                sacks_received=data["sacks_received"],
                logged_by=session["user_id"],
            )
            db.session.add(receipt)
            db.session.commit()
            return inventory_receipt_schema.dump(receipt), 201
        except (KeyError, ValueError) as e:
            db.session.rollback()
            return {"error": str(e)}, 422


class InventoryReceiptByID(Resource):
    @manager_required
    def patch(self, id):
        receipt = InventoryReceipt.query.get_or_404(id)
        data = request.get_json() or {}
        if "sold_out" in data:
            receipt.sold_out = bool(data["sold_out"])
        db.session.commit()
        return inventory_receipt_schema.dump(receipt), 200
