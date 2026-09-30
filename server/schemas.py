from marshmallow import Schema, fields, validate, validates_schema, ValidationError

from models.sack_item import VALID_SIZES, VALID_SERVICES, VALID_COLOR_STAGES, VALID_VARIETIES
from models.inventory_receipt import VALID_INVENTORY_VARIETIES


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    role = fields.Str(validate=validate.OneOf(["employee", "manager"]))
    # password_hash is intentionally never a field here -- it must never be serialized,
    # even by accident, since SQLAlchemyAutoSchema-style tools would include it by default.


class SackItemSchema(Schema):
    id = fields.Int(dump_only=True)
    order_id = fields.Int(dump_only=True)
    size = fields.Str(required=True, validate=validate.OneOf(VALID_SIZES))
    service = fields.Str(required=True, validate=validate.OneOf(VALID_SERVICES))
    color_stage = fields.Str(required=True, validate=validate.OneOf(VALID_COLOR_STAGES))
    variety_1 = fields.Str(required=True, validate=validate.OneOf(VALID_VARIETIES))
    variety_2 = fields.Str(allow_none=True, validate=validate.OneOf(VALID_VARIETIES))
    addon_note = fields.Str(allow_none=True)
    queue_sequence = fields.Int(dump_only=True)
    sack_status = fields.Str(dump_only=True)
    estimated_finish_at = fields.DateTime(dump_only=True)
    actual_finish_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_mix_rules(self, data, **kwargs):
        """This is the authoritative check for the business's mixing rules:
        a half-sack can never be mixed, and a full sack can mix at most two
        DIFFERENT varieties. Runs on the full payload at once, so it isn't
        subject to field-assignment-order issues the model-level validators
        can have.
        """
        variety_2 = data.get("variety_2")
        if variety_2:
            if data.get("size") == "half_sack":
                raise ValidationError("Half sacks cannot be mixed.", field_name="variety_2")
            if variety_2 == data.get("variety_1"):
                raise ValidationError("variety_2 must differ from variety_1.", field_name="variety_2")


class OrderSchema(Schema):
    id = fields.Int(dump_only=True)
    display_number = fields.Int(dump_only=True)
    business_date = fields.Date(dump_only=True)
    customer_name = fields.Str(allow_none=True)
    contact_info = fields.Str(allow_none=True)
    status = fields.Str(dump_only=True)
    manager_note = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    created_by = fields.Int(dump_only=True)
    sack_items = fields.List(fields.Nested(SackItemSchema), dump_only=True)


class SeasonSchema(Schema):
    id = fields.Int(dump_only=True)
    year = fields.Int(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)


class InventoryReceiptSchema(Schema):
    id = fields.Int(dump_only=True)
    variety = fields.Str(required=True, validate=validate.OneOf(VALID_INVENTORY_VARIETIES))
    color_stage = fields.Str(required=True, validate=validate.OneOf(VALID_COLOR_STAGES))
    sacks_received = fields.Float(required=True)
    date_received = fields.Date(dump_only=True)
    sold_out = fields.Bool()
    logged_by = fields.Int(dump_only=True)


user_schema = UserSchema()
users_schema = UserSchema(many=True)

sack_item_schema = SackItemSchema()
sack_items_schema = SackItemSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

season_schema = SeasonSchema()
seasons_schema = SeasonSchema(many=True)

inventory_receipt_schema = InventoryReceiptSchema()
inventory_receipts_schema = InventoryReceiptSchema(many=True)
