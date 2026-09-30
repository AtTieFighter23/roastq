from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from config import Config
from extensions import db, bcrypt, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Explicit origin list required alongside supports_credentials=True --
    # browsers reject wildcard origins on credentialed requests. Both
    # localhost and 127.0.0.1 are listed because browsers treat them as
    # different origins even on the same machine.
    CORS(app, supports_credentials=True, origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ])

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # A fresh Api instance per call, NOT a shared module-level singleton.
    # Flask-RESTful's Api replays every previously-registered resource onto
    # whatever app it's (re-)bound to, so a shared Api would silently
    # re-register every route a second time if create_app() is ever called
    # more than once in the same process -- which seed.py does today, and
    # which any future pytest suite will do routinely.
    api = Api(app)

    # Import every model so Flask-Migrate/SQLAlchemy's mapper registry sees
    # them all before anything queries the database.
    from models import user, season, order, sack_item, queue_adjustment, inventory_receipt  # noqa: F401

    register_routes(api)

    return app


def register_routes(api):
    from resources.auth import Login, Logout, CheckSession
    from resources.users import Users
    from resources.orders import Orders, OrderByID
    from resources.sack_items import OrderSackItems, SackItemByID
    from resources.queue import PublicQueue, QueueDelay, QueueThroughputMode, QueueReorder, QueueNote
    from resources.seasons import Seasons, SeasonByID
    from resources.inventory import InventoryReceipts, InventoryReceiptByID

    api.add_resource(Login, "/api/login")
    api.add_resource(Logout, "/api/logout")
    api.add_resource(CheckSession, "/api/check_session")
    api.add_resource(Users, "/api/users")

    api.add_resource(Orders, "/api/orders")
    api.add_resource(OrderByID, "/api/orders/<int:id>")
    api.add_resource(OrderSackItems, "/api/orders/<int:order_id>/sack_items")
    api.add_resource(SackItemByID, "/api/sack_items/<int:id>")

    api.add_resource(PublicQueue, "/api/queue")
    api.add_resource(QueueDelay, "/api/queue/delay")
    api.add_resource(QueueThroughputMode, "/api/queue/mode")
    api.add_resource(QueueReorder, "/api/queue/reorder")
    api.add_resource(QueueNote, "/api/queue/note")

    api.add_resource(Seasons, "/api/seasons")
    api.add_resource(SeasonByID, "/api/seasons/<int:id>")

    api.add_resource(InventoryReceipts, "/api/inventory")
    api.add_resource(InventoryReceiptByID, "/api/inventory/<int:id>")


app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)
