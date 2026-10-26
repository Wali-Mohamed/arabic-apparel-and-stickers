# Neon PostgreSQL and Vercel preparation

Neon has been created by the owner. This change prepares local configuration;
the agent has not received/read a real connection string, connected to Neon,
executed migrations (including local ones), changed Vercel settings or deployed.

## Two separate connection purposes

| Purpose | Variable | Connection |
| --- | --- | --- |
| FastAPI requests | DATABASE_URL | Copy the pooled connection for the intended Neon branch/database from its Connect dialog; pooler host normally ends in -pooler before the domain |
| Operator migrations | MIGRATION_DATABASE_URL | Copy the direct connection from the same branch/database with pooling disabled; use a migration-capable role |

Use `postgresql+psycopg://` with the installed psycopg 3 driver. The configuration
also normalizes `postgresql://` or `postgres://` to that driver. Do not change the
host, branch/database, percent-encoded credentials or SSL query options copied
from the console. In particular retain `sslmode=require` and any
`channel_binding=require` option supplied by Neon. No actual URL is shown here.

The new connection-only `app/db_config.py` never opens a socket. It adds
sslmode=require for recognized .neon.tech hosts when absent, preserves stronger
verify-ca/verify-full settings and rejects SSL disable/allow/prefer for those
hosts. DATABASE_SSL_REQUIRED=1 also enforces this for custom endpoint names.
SSL require enforces encryption; full certificate/hostname verification requires
verify-full and appropriate trust configuration. No SSL handshake has been
tested against the actual database in this task.

For the pooled URL or VERCEL=1, SQLAlchemy defaults to NullPool: sessions close
their client connection rather than retain a pool in each serverless instance;
Neon's external pooler performs pooling. DATABASE_POOL_MODE=null explicitly
selects this policy. Local Docker retains QueuePool and its existing non-SSL
private database connection. DB sessions remain request-scoped and close in
get_db's finally block; no ORM/API replacement is needed.

Connection attempts have a 10-second connection timeout for recognized Neon or
Vercel runtime settings. Automatic psycopg prepared statements are disabled for
pooler endpoints as a conservative choice with the pinned driver/libpq, not
because Neon universally lacks protocol prepared statement support. Do not rely
on session-level SET, temporary-table state or session advisory locks through a
transaction pooler. No automatic retry of order writes is added: a retry after
an ambiguous commit can duplicate an order.

## Environment and secret handling

`.env.neon.example` contains blank placeholders only. Set real values in private
environment/secret storage; real .env.* and .vercel files are ignored by Git.
The application does not automatically source a plaintext .env file: export
variables with the operator's secure tooling, or let the hosting platform inject
them. Never echo/printenv the URLs or put passwords in command-line arguments.
DATABASE_URL must never be exposed as VITE_DATABASE_URL or another frontend key.

Vercel backend runtime variables to configure later:

- DATABASE_URL: pooled Neon URL, ideally a least-privilege runtime login.
- DATABASE_POOL_MODE=null and DATABASE_SSL_REQUIRED=1.
- APP_ENV=production (also defaulted by the dedicated ASGI entrypoint).
- PUBLIC_ORIGIN: exact HTTPS frontend origin.
- ALLOWED_HOSTS: actual backend hostname(s), no wildcard/scheme/port.

Vercel provides VERCEL=1 itself. Keep MIGRATION_DATABASE_URL in an operator-only
secret context, not the frontend or Vercel runtime. Preview and production must
use the intended separate Neon branches and appropriately scoped environment
variables; do not let untrusted PR previews write into the production database.
No Vercel/GitHub environment settings are changed by this preparation.

## Safe migration and seeding procedure (planned, not executed)

First inspect the target branch/database in Neon Console and take a branch/
snapshot or backup as appropriate. Prefer a fresh dedicated application database;
do not apply this catalogue history to an unrelated populated database. Read
the revision files before execution: historical revisions do change/delete
obsolete catalogue rows. None of those revisions were modified by this task.

The existing six Alembic revisions create and seed products, prices, orders and
options. `alembic_version` records which revisions ran, so a second upgrade to
head does not replay seed revisions. There is no separate destructive reset or
unconditional reseed command. Future schema/seed changes need a NEW revision.

From the repository checkout with backend requirements installed, first run:

```powershell
# Requires MIGRATION_DATABASE_URL already injected privately.
# Default mode only parses configuration and reads local revision metadata.
python backend/migrate_neon.py
```

This default validation does NOT connect, fetch database revision state or test
credentials/SSL connectivity. It rejects missing/direct-pooler/unsafe SSL
configuration and prints only the local migration head, not a URL or password.

Only after explicit approval to connect and migrate, the operator can run:

```powershell
# Planned ONLY. Replace these non-secret target labels with the verified target.
python backend/migrate_neon.py --apply --expected-host DIRECT_HOST_FROM_CONSOLE --expected-database DATABASE_NAME_FROM_CONSOLE
```

`--apply` requires a direct MIGRATION_DATABASE_URL and exact host/database
confirmation BEFORE an engine is created. The helper uses one direct NullPool
connection, takes a session advisory lock, upgrades to head and verifies head,
eight seeded products and ten price rows. It does not delete/reset order data.
Coordinate ALL migration operators through this helper: a separate raw Alembic
invocation will not honor its lock. Initial migrations can be re-invoked safely
once applied; this is versioned migration repeatability, not proof of recovery
from every interrupted/partially applied migration. On failure, investigate before
retrying; verification failure can occur after successful committed migrations.
Future intentional catalogue changes must update the verification expectations.

The helper suppresses exception dumps because driver exceptions may contain
credentials or customer data. Read its generic result and inspect privileged
diagnostics carefully rather than dumping environment/URLs into shared logs.
No actual apply/lock/seed verification path has been exercised in this task.

Alembic now resolves its paths relative to alembic.ini, selects the direct URL
independently of app.database, and retains percent escaping and NullPool.
The provided-connection path lets the helper hold one advisory-lock session.
Normal local `docker compose exec backend alembic upgrade head` still selects
the local DATABASE_URL when no migration URL is supplied. Do not run that local
startup command with Neon variables accidentally exported into a development
container: Docker's development entrypoint automatically migrates on startup.
No local migration or Docker stack startup was run during this task.

Never migrate in a FastAPI import, lifespan event, Vercel build, request handler
or cold start. Never stamp an existing database to head merely to silence errors.
Do not downgrade/restore over orders without a separately approved recovery plan.

## Vercel Hobby: one project, two services

The owner reports the Neon database reached revision `20261025_06` and catalogue
seed verification passed. This is owner-reported evidence, not a connection made
by this agent. Do not rerun migrations for deployment; migrations never run in
builds, imports or requests.

Root `vercel.json` defines frontend (Vite) and backend (FastAPI) services.
Vercel Services is currently beta and available on all plans, including Hobby.
API rewrites run before the frontend catch-all and preserve the original path.
`backend/asgi.py` exports `app` with production defaults. `/api/products`, pricing
and orders retain their existing paths. `/api/health` and `/api/health/db` are
health aliases; `/health` and `/health/db` remain supported for Docker.
Unknown API paths must return API 404, never React HTML. The frontend service's
own rewrite provides index.html for client-side navigation, excluding assets.
The current React application has no URL router; deep links load its catalogue,
not a product-specific page. Missing assets must remain 404.

Production builds default to same-origin API requests; development retains
localhost:8000 unless VITE_API_BASE_URL is supplied. Leave that build variable
unset on Vercel. No database variable may have a VITE_ prefix. Vite serves only
local development; Vercel serves compiled dist assets from its CDN. Nginx and
Compose are not used by Vercel; both Docker configurations remain supported.

### Exact GitHub import steps (future, not performed)

1. Independently review this local diff, then separately authorize commit/push.
   Vercel cannot import unpublished local changes. Do not import now: clicking
   Deploy or linking Git can create deployments independently of GitHub CD holds.
2. When deployment is authorized, open Vercel > Add New > Project > Import Git
   Repository > Wali-Mohamed/arabic-apparel-and-stickers. Select Hobby only for
   a personal, non-commercial capstone demonstration.
3. Set Root Directory to repository root (`./`), not frontend/ or backend/.
   Use Other at the top level if a preset is requested. The root services config
   supplies each service framework; do not override root install/build/output.
   Frontend: Node 22.x, npm ci, npm run build, dist. Backend: Python 3.12 from
   backend/.python-version, requirements.txt, FastAPI entrypoint asgi:app;
   no custom Uvicorn/start command, no Docker build, no Alembic build command.
   If Services beta requires an account opt-in, enable it only during authorized
   setup. Do not silently fall back to a frontend-only deployment.
4. Select/reserve the actual project domain before deployment. In project
   Environment Variables add the values below, scoped only to the intended
   environment. PUBLIC_ORIGIN/ALLOWED_HOSTS must describe the domain actually
   used to open the app. Do not use wildcard hosts or assume generated preview
   domains are covered. Disable unwanted Git auto-deploys/previews before
   publishing changes; use separate Neon branches/roles and exact origins for
   previews. Do not grant fork previews production credentials.
5. Choose a function region close to Neon where the plan allows; verify runtime
   settings in the dashboard. Configure edge abuse controls before public use.
   This configuration does not replicate Nginx's body-size/rate limits.
6. Only after separate deployment authorization, click Deploy. Check both service
   build logs without printing environment values. Record the real URL and build
   evidence. If no domain was reserved, update origin/hosts to the actual assigned
   domain and redeploy before exercising the API.
7. Verify GET /api/health returns 200, GET /api/health/db returns 200 and
   GET /api/products returns eight products; /api/missing returns JSON 404;
   a client deep link returns React HTML and /assets/missing.js returns 404.
   Verify Arabic customization, quantity/pair pricing and one synthetic order
   persists in the intended database. Never use real customer contact details.
   Check foreign Origin POSTs are rejected. These hosted checks are pending.

| Variable | Vercel runtime value |
| --- | --- |
| DATABASE_URL | Private pooled Neon URL, postgresql+psycopg:// scheme, SSL options retained; preferably least-privilege runtime role |
| DATABASE_POOL_MODE | null |
| DATABASE_SSL_REQUIRED | 1 |
| APP_ENV | production |
| PUBLIC_ORIGIN | Exact actual HTTPS app origin, no path or trailing slash |
| ALLOWED_HOSTS | Comma-separated actual app hostnames, no scheme, port or wildcards |

Vercel injects VERCEL=1. Do not add MIGRATION_DATABASE_URL to Vercel: it remains
operator-only. Store DATABASE_URL only using Vercel's private environment UI;
never in GitHub files, screenshots, chat, frontend configuration or build commands.
Never print environments in logs. Runtime secrets share the project environment;
ensure frontend source never references or copies them into build artifacts.

### Hobby constraints and release gates

- Hobby is for personal non-commercial use. This capstone must remain a demo,
  not a real apparel sales/order-taking business. Reassess plan eligibility before
  accepting real orders, even though payment and checkout are absent.
- Services is beta: an actual Vercel build/routing smoke test remains required.
  Offline tests cannot prove platform discovery, CDN or forwarded Host behavior.
- Functions are stateless, may cold-start and have ephemeral filesystems. Store
  orders only in Neon. No persistent workers, local PostgreSQL or background
  fulfillment. Neon suspension can add cold-start latency.
- Hobby functions have 2 GB memory; with Fluid Compute, Python's maximum duration
  is 300 seconds; legacy non-Fluid limits differ. Request/response bodies are
  limited to 4.5 MB and Python bundles to 500 MB. Verify current dashboard limits.
  Never run migrations or long jobs inside requests.
- NullPool plus Neon's pooled endpoint avoids per-instance retained SQLAlchemy
  pools, but bursts can still exhaust database/client limits. Monitor usage,
  configure abuse limits and retain the request-scoped session cleanup. Never
  automatically retry an ambiguously committed order: duplicates are possible.
- Demo orders are unauthenticated and not idempotent. CORS/Origin checks are not
  authentication or bot protection. Use synthetic data, limit access/abuse and
  define retention before any public demonstration. Hobby quotas can suspend
  service until usage windows reset; do not promise availability.
- Root config adds CSP/security headers and API no-store. Vercel does not inherit
  Nginx request throttling; edge protections, privacy review and live HTTPS/header
  checks remain required. GitHub deployment holds are unchanged and do not gate
  Vercel's independent Git integration.
- Application rollback uses a previous compatible Vercel deployment; it does not
  reverse Neon data/schema. Use forward-compatible migrations and separately
  approved database recovery. Independent review remains outstanding.

Official references checked for this preparation:
[Vercel Services configuration and availability](https://vercel.com/kb/guide/vercel-services),
[Vercel FastAPI](https://vercel.com/docs/frameworks/backend/fastapi),
[Vercel Hobby](https://vercel.com/docs/plans/hobby),
[Function limits](https://vercel.com/docs/functions/limitations),
[Neon pooling](https://neon.com/docs/connect/connection-pooling).
