# RoastQ

A full-stack order and queue management system for a seasonal chile-roasting
operation. Built as the final capstone project (Full-Stack Application with
Auth) for the Flatiron SE-FT-ACP-01 program.

## Project description

During the two-month green/red chile harvest season, a small gift-shop
business also roasts and sells fresh peppers. Orders today are tracked on
paper, color-coded tickets, which pulls staff off the floor whenever a
customer asks for a status update, and leaves no historical sales data to
plan future seasons' purchasing. RoastQ replaces that with:

- A **public, no-login queue board** customers can check themselves by their
  order number (no personal information ever displayed).
- An **authenticated staff dashboard** (Employee / Manager roles) for
  creating orders, managing the roasting/peeling queue, and reviewing
  historical sales and inventory data.

See `PROJECT_BRIEF.md` (or the original Project Pitch) for the full business
problem writeup, data model diagrams, and rubric mapping.

## Tech stack

- **Backend:** Flask, Flask-RESTful, Flask-SQLAlchemy, Flask-Migrate,
  Flask-Bcrypt, Marshmallow, session-based auth
- **Database:** SQLite for this prototype, built entirely on the SQLAlchemy
  ORM so a future move to PostgreSQL is a configuration change, not a
  rewrite (set `DATABASE_URL` in `.env`)
- **Frontend:** React (Vite), React Router

## Project structure

```
roastq/
├── server/          Flask API (see server/README section below)
│   ├── models/
│   ├── resources/
│   ├── services/
│   └── app.py
└── client/          React (Vite) frontend
    └── src/
```

## Setup and run instructions

### Backend

```bash
cd server
cp .env.example .env      # edit SECRET_KEY; leave DATABASE_URL blank for SQLite
pipenv install
pipenv shell
export FLASK_APP=app.py
flask db init              # first time only
flask db migrate -m "initial schema"
flask db upgrade           # migrations own the schema -- always run these BEFORE seeding
python seed.py             # inserts 1 manager, 1 employee, and the 2026 season (data only, safe to re-run)
python app.py               # runs on http://localhost:5555
```

Order matters here: `seed.py` only ever inserts rows, it never creates tables.
If you run it before the migration steps, Flask-Migrate will find a database
that already matches the models and skip generating your initial migration
entirely ("No changes in schema detected") -- always migrate first, on an
empty database.

Seeded accounts (change immediately in any non-local environment):

| username    | password      | role     |
|-------------|---------------|----------|
| manager1    | changeme123   | manager  |
| employee1   | changeme123   | employee |

### Frontend

```bash
cd client
npm install
npm run dev                # runs on http://localhost:5173, proxies /api to :5555
```

Open `http://localhost:5173` for the public queue board, or `/login` to sign
in as staff.

## Feature overview (scaffold status)

Working now:
- Session-based auth (login / logout / check_session) with Employee vs.
  Manager roles enforced via decorators
- Full data model: `User`, `Season`, `Order`, `SackItem`,
  `QueueAdjustment` (audit log), `InventoryReceipt`
- Order + SackItem CRUD with sack-mixing business rules enforced at the
  schema layer (half-sacks can't mix; full sacks mix at most 2 varieties)
- Daily-reset order numbers (`display_number` unique per `business_date`,
  while the internal `id` stays permanent for history/analytics)
- Queue timing engine: throughput-mode math (normal / degraded / halted),
  manager-only reorder, employee-or-manager flat delay minutes
- Public, no-login queue board (polling) and a role-aware authenticated
  dashboard shell

Planned next (see project pitch timeline):
- Full order-entry UI and manager queue-control UI
- Browser notifications ("notify me when ready")
- Season and inventory management screens
- QR-code generation linking to a specific order's queue view

## API routes

All routes are namespaced under `/api`. Routes marked (public) require no
authentication; everything else requires a logged-in session, and (manager)
routes additionally require the `manager` role.

- `POST /api/login`, `DELETE /api/logout`, `GET /api/check_session`
- `GET/POST /api/users` (manager)
- `GET/POST /api/orders`, `GET/PATCH/DELETE /api/orders/<id>`
- `POST /api/orders/<order_id>/sack_items`, `PATCH/DELETE /api/sack_items/<id>`
- `GET /api/queue` (public)
- `POST /api/queue/delay`, `POST /api/queue/note`
- `POST /api/queue/mode` (manager), `POST /api/queue/reorder` (manager)
- `GET/POST /api/seasons` (manager), `PATCH /api/seasons/<id>` (manager)
- `GET/POST /api/inventory` (manager), `PATCH /api/inventory/<id>` (manager)

## Notes on this scaffold

This backend was written and syntax-verified in a sandboxed environment
without package-registry access, so it has **not yet been run end-to-end**.
The very first thing to do after pulling this in locally is the standard
verify-locally step: run the seed script and start the server, then confirm
`GET /api/check_session`, `POST /api/login`, and `GET /api/queue` behave as
expected before building UI on top of it.
