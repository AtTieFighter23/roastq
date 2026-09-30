import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # Defaults to a local SQLite file; set DATABASE_URL in .env to point at
    # PostgreSQL later without touching any application code.
    #
    # NOTE: this must be `os.environ.get("DATABASE_URL") or default`, not
    # `os.environ.get("DATABASE_URL", default)`. Pipenv auto-loads .env, and
    # .env.example ships with `DATABASE_URL=` (empty). The two-argument form
    # of .get() only falls back to `default` when the key is missing
    # entirely -- an empty string still counts as "present," so it was being
    # returned as-is and SQLAlchemy correctly rejected it as an unparseable URL.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        f"sqlite:///{os.path.join(INSTANCE_DIR, 'roastq.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cross-port session cookies (Vite dev server -> Flask API) require these,
    # even over local http -- see project notes on CORS + session cookies.
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SECURE = True
