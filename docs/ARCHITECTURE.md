# Architecture

## Components

- **Frontend:** React 18, TypeScript, and Vite provide the catalogue, product customizer, RTL preview, quote display, and order-request form.
- **Backend:** FastAPI exposes health, product, pricing, and order-request APIs.
- **Database:** PostgreSQL 16 stores catalogue records, option-aware pence prices, and admin order requests.
- **Persistence:** The default Compose stack mounts PostgreSQL data at the named `postgres-data` volume.
- **Orchestration:** Docker Compose builds and starts `frontend`, `backend`, and `postgres`. The backend waits for PostgreSQL health and applies Alembic migrations before starting Uvicorn.

## API flow

The frontend shares one isolated LTR Be Seen design renderer across Small/Big
tag cards, live previews, order summaries and confirmations. English and Arabic
remain separate bidi isolates; Arabic shaping is preserved. This presentation
change needs no catalogue migration or API payload change.

1. The frontend loads `GET /api/products`.
2. Product selections are submitted to `POST /api/products/{id}/price` with options and quantity.
3. FastAPI validates Arabic text and allowed options, reads the matching `product_prices` row, and calculates any pair discount.
4. The frontend displays the server quote.
5. The order form sends customer contact details, selections, and quantity to `POST /api/orders`.
6. FastAPI repeats validation and price calculation, then persists an `orders` row with `new` status.

## Database schema

- `products`: product slug, name, category, description, and configuration options JSON.
- `product_prices`: product option key/value, unit price in pence, and optional pair price in pence.
- `orders`: product reference, customer name/contact, selected options JSON, quantity, calculated total in pence, status, and timestamp.
- `alembic_version`: current migration revision.

## Production configuration

The standalone `compose.production.yml` uses separate production Dockerfiles;
the original development stack keeps its source mounts and hot reload. Nginx
serves the Vite dist build and proxies same-origin `/api/` and health endpoints
to a private non-reloading two-worker FastAPI service. An explicit migration
job runs first. PostgreSQL and the API have no published ports and use private
networks; only the frontend can bind a host socket (loopback by default).
Hosting this standalone Docker variant still requires a trusted TLS edge, DNS
and operator secrets. The existing public deployment uses Vercel and Neon instead.
Production requires exact PUBLIC_ORIGIN/ALLOWED_HOSTS and database credentials;
it disables API docs, rejects foreign write Origins, validates Host and hides SQL
parameters. No database schema changes are introduced. See the
[production runbook](PRODUCTION_DEPLOYMENT.md) for security limits and smoke tests.

## Development networking

- Browser: `http://localhost:5173`
- FastAPI: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

`VITE_API_BASE_URL` must point to the browser-reachable FastAPI address. Docker service-to-service database traffic uses the `postgres` hostname on the Compose network.

## CI/CD validation and deployment boundary

GitHub Actions CI runs backend, frontend, build and PostgreSQL integration jobs
on pull requests and main pushes. Integration uses an ephemeral PostgreSQL
service upgraded by Alembic, separate from developer/hosted data. `compose.ci.yml`
provides a disposable local equivalent. The prepared development job listens for
successful main CI; the production job uses manual dispatch. Both GitHub jobs
remain explicitly held pending adapter/approval configuration. The separate
Vercel Git integration reports deployment success for main/e9d8ef9, and the owner
screenshot shows its production alias. Automatic push triggering is inferred,
not independently confirmed by provider audit metadata. This deployment completed
before all CI jobs finished; successful CI is not evidence of a Vercel CI gate.
See [CI/CD and rollback](CI_CD.md) for permissions, setup and current blockers.

## Neon/Vercel connection boundary

Hosted connection setup is documented in [Neon/Vercel](NEON_VERCEL.md).
Pure db_config parsing preserves psycopg/SSL query settings, chooses NullPool
for serverless/pooler runtime connections and keeps local QueuePool behavior.
Alembic selects MIGRATION_DATABASE_URL independently from the pooled app URL;
no migration runs on ASGI import or request startup. The operator helper defaults
to a no-connect plan and requires explicit apply/target confirmation to migrate.
Root vercel.json defines frontend Vite and backend FastAPI Vercel Services
(currently beta). Ordered rewrites preserve /api paths and health endpoints;
the frontend service handles SPA fallback. Production frontend builds default
to same-origin requests; local development keeps its localhost API default.
The public Vercel/Neon application has recorded health, catalogue, quote and
synthetic-order results. An owner-supplied screenshot shows Production / Ready,
main/e9d8ef9 and the public domain at capture time. See
[submission evidence](SUBMISSION.md) for verified facts and trigger uncertainty;
no independent provider-settings audit or hosted rollback is claimed.

## Local observability

Optional local telemetry uses manual request/business spans, JSON completion
logs and request/error/duration metrics. The standalone compose.observability.yml
sends OTLP to pinned LGTM storage/UI and uses its own tmpfs PostgreSQL. Existing
Compose/Vercel settings are untouched; instrumentation is disabled by default.
See [local observability](OBSERVABILITY.md) for privacy boundaries and evidence.

## Local alerting

The optional alerting overlay provisions PricingUnavailable against the existing
pricing request counter and routes notifications only to an internal sanitizing
webhook. Its marker-based 503 fault is guarded by explicit local flags and the
disposable database identity; no public control endpoint or database write is
introduced. See [local alerting](ALERTING.md) for recovery and evidence boundaries.

## Local on-call responder

The optional standalone oncall overlay extends local observability with an
authenticated webhook, SQLite incident ledger and bounded Ollama decision worker.
A dedicated disposable fault volume is shared only with the isolated backend;
the worker has no database or cloud credentials or Docker socket. Runtime uses
an internal network, while a separate setup service downloads the local model.
The original alerting demonstration is preserved. See [on-call runbook](ONCALL.md)
for tools, permission gates, actual execution evidence and remaining review work.

## Migration strategy

Alembic revisions are linear. Local Compose runs them at backend startup; the
standalone production stack has a separate migration job. Vercel does not migrate
on import or requests; hosted migrations are a separately authorized operator
action. Revisions create the base catalogue, add prices and pair offers, create
order requests, update the fixed Be Seen display, and seed HTV colours. The
JSON/JSONB cast in revision `20261025_06` supports PostgreSQL's `jsonb_set` function
while retaining the existing JSON column type.
