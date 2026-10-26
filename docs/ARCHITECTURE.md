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

## Local networking

- Browser: `http://localhost:5173`
- FastAPI: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

`VITE_API_BASE_URL` must point to the browser-reachable FastAPI address. Docker service-to-service database traffic uses the `postgres` hostname on the Compose network.

## Migration strategy

Alembic revisions are linear and are run on backend startup. Revisions create the base catalogue, add prices and pair offers, create order requests, update the fixed Be Seen display, and seed HTV colours. The JSON/JSONB cast in revision `20261025_06` supports PostgreSQL's `jsonb_set` function while retaining the existing JSON column type.
