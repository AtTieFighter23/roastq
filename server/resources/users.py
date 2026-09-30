from flask import request
from flask_restful import Resource

from extensions import db
from models.user import User
from schemas import user_schema, users_schema
from decorators import manager_required


class Users(Resource):
    @manager_required
    def get(self):
        return users_schema.dump(User.query.order_by(User.username).all()), 200

    @manager_required
    def post(self):
        """Lets a manager add a new hire's account mid-season -- there is no
        public signup endpoint, since the business only ever has a handful of
        staff accounts and account creation should stay manager-controlled.
        """
        data = request.get_json() or {}
        try:
            new_user = User(username=data["username"], role=data.get("role", "employee"))
            new_user.password_hash = data["password"]
            db.session.add(new_user)
            db.session.commit()
            return user_schema.dump(new_user), 201
        except (KeyError, ValueError) as e:
            db.session.rollback()
            return {"error": str(e)}, 422
