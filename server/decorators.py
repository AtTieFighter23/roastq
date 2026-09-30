from functools import wraps

from flask import session

from models.user import User


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return {"error": "Unauthorized. Please log in."}, 401
        return f(*args, **kwargs)
    return wrapper


def manager_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized. Please log in."}, 401
        user = User.query.get(user_id)
        if not user or user.role != "manager":
            return {"error": "Manager access required."}, 403
        return f(*args, **kwargs)
    return wrapper
