# Product Specification

## Purpose

Arabic Apparel and Stickers is a catalogue and admin-order-request demo for Arabic-personalized HTV products, Be Seen tags, sweaters, and canvas bags.

## Scope

- Browse the eight-item catalogue and see demonstration GBP prices.
- Personalize supported products with validated Arabic text, fonts, sizes, and HTV colours.
- Receive a backend-calculated quote that supports pair offers.
- Submit an admin-review order request to PostgreSQL.

Payments, customer accounts, checkout, fulfillment, and production-accurate rendering are not in scope.

## Product rules

- Small and Big Be Seen tags display English `Be` on the left and Arabic `س` on
  the right in an explicit LTR container with isolated script spans. Cards,
  previews, order summaries and confirmations use the same fixed, non-editable design.
- The rectangular tag supports Arabic names up to 24 graphemes.
- The small letter-only tag accepts exactly one Arabic letter plus optional diacritics.
- HTV sizes are 5 x 5, 9 x 4, and 12 x 3 inches.
- Personalized text uses Amiri, Cairo, or Tajawal and is Unicode NFC normalized.
- Text must contain an Arabic letter. Diacritics, spaces, hyphens, Arabic digits, and Western digits are allowed; Latin characters, emoji, and unsupported symbols are rejected.
- The backend validates every submitted option and calculates the price in integer pence.

## Acceptance criteria

1. `GET /api/products` returns the eight current products, their options, and pence prices.
2. `POST /api/products/{id}/price` rejects invalid options and returns a server-calculated total for a positive quantity.
3. Pair offers apply to each complete pair; any odd item uses its standard unit price.
4. The React UI renders RTL Arabic previews, accessible input labels, validation feedback, product prices, and a mobile-friendly customizer.
5. The HTV customizer offers the twenty documented colour choices and the three inch-size options.
6. `POST /api/orders` recalculates the submitted price, saves the order request with status `new`, and never accepts a client price.
7. Alembic migrates an empty PostgreSQL database to the latest revision without manual SQL.
8. Backend and frontend automated tests pass, and the frontend production build succeeds.

## Delivery validation

Optional local observability must correlate sanitized request logs and spans,
collect request/error/duration metrics and expose them in a monitoring UI.
Never record personalization/contact data, bodies, credentials or SQL parameters;
exporter failure must not interrupt ordering. Local evidence and unverified
metric-exemplar or production-monitoring claims must remain explicitly distinct.

CI must run backend tests, isolated PostgreSQL integration after Alembic
migrations, frontend tests/build using the committed npm lockfile, and Docker
image builds on pull requests and pushes to main. Deployment preparation must
separate automatic development from manually approved production and document
rollback. Hosting remains unconfigured; no public deployment is authorized by
this specification. See [CI/CD setup](docs/CI_CD.md) for outstanding prerequisites.

## Production preparation acceptance criteria

1. Separate production images build Vite static assets and serve them with a
   production web server, while development hot reload remains available.
2. Browser API traffic stays same-origin through a reverse proxy; FastAPI runs
   without auto-reload and PostgreSQL has no public port.
3. Production requires explicit credentials, trusted hosts and exact origin;
   health checks and a separate migration job gate startup.
4. Isolated production-style browser tests demonstrate browsing, RTL Arabic
   personalization, server pricing and persisted synthetic orders, security
   rejection paths and API restart persistence.
5. Hosting/TLS setup, resource/cost estimates, rollback and outstanding public
   deployment evidence are documented without claiming a live deployment.

## Neon/Vercel preparation boundary

Runtime and migration credentials must remain distinct environment inputs;
Neon URLs preserve SSL requirements and the psycopg driver. Preparation must not
connect, migrate or seed until separately authorized. Local Docker/PostgreSQL
remains supported. See [Neon/Vercel preparation](docs/NEON_VERCEL.md).

The Vercel variant uses repository-root Services routing: Vite static frontend,
same-origin FastAPI /api and /api/health endpoints, and pooled Neon runtime
connections. SPA fallback must not capture unknown API paths. The owner reports
revision 20261025_06 and catalogue verification passed; hosted verification and
independent review remain pending. Hobby use is limited to a non-commercial demo.
