# Architecture

## Components

- **Frontend:** React 18, TypeScript, and Vite provide the catalogue, product customizer, RTL preview, quote display, and order-request form.
- **Backend:** FastAPI exposes health, product, pricing, and order-request APIs.
- **Database:** PostgreSQL 16 stores catalogue records, option-aware pence prices, and admin order requests.
- **Persistence:** The default Compose stack mounts PostgreSQL data at the named `postgres-data` volume.
- **Orchestration:** Docker Compose builds and starts `frontend`, `backend`, and `postgres`. The backend waits for PostgreSQL health and applies Alembic migrations before starting Uvicorn.

## API flow

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
An external trusted TLS edge, DNS, secrets and hosting still need configuration.
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
provides a disposable local equivalent. Development CD follows successful main
CI; production CD uses a manual dispatch and requires environment protection
configured by the owner. Both remain disabled pending a real hosting adapter.
See [CI/CD and rollback](CI_CD.md) for permissions, setup and current blockers.

## Migration strategy

Alembic revisions are linear and are run on backend startup. Revisions create the base catalogue, add prices and pair offers, create order requests, update the fixed Be Seen display, and seed HTV colours. The JSON/JSONB cast in revision `20261025_06` supports PostgreSQL's `jsonb_set` function while retaining the existing JSON column type.
