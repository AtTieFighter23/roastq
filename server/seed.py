from datetime import date

from app import app
from extensions import db
from models.user import User
from models.season import Season

# NOTE: this file only ever INSERTS data. It must never call db.drop_all()/
# db.create_all() -- schema creation belongs entirely to Flask-Migrate
# (flask db init/migrate/upgrade). If this seed script also builds tables
# directly, Alembic sees a database that already matches the models by the
# time you run `flask db migrate`, so it reports "No changes in schema
# detected" and never generates the initial migration -- which then leaves
# you with no migration history and no alembic_version tracking table.
# Always run the migration commands FIRST, on an empty/nonexistent database,
# and only run this script afterward.

with app.app_context():
    if User.query.filter_by(username="manager1").first():
        print("Already seeded (manager1 exists) -- skipping to avoid duplicate/unique-constraint errors.")
        print("If you want a clean reset instead, delete instance/roastq.db and re-run the migration steps.")
    else:
        manager = User(username="manager1", role="manager")
        manager.password_hash = "changeme123"

        employee = User(username="employee1", role="employee")
        employee.password_hash = "changeme123"

        db.session.add_all([manager, employee])

        current_season = Season(year=2026, start_date=date(2026, 8, 1), end_date=date(2026, 10, 1))
        db.session.add(current_season)

        db.session.commit()
        print("Seeded: 1 manager (manager1), 1 employee (employee1), 2026 season. Password for both: changeme123")
