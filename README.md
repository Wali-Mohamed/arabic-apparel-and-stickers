# Arabic Apparel and Stickers

A React, FastAPI, and PostgreSQL capstone for Arabic-personalized apparel, tags, and HTV stickers. Prices are demonstration GBP prices; no payment processing is implemented.

## Live demo

Open [Arabic Apparel and Stickers](https://arabic-apparel-and-stickers.vercel.app/).
This is a personal, non-commercial capstone demonstration: no payments, checkout
or fulfillment. Use synthetic contact details only; submitting an order creates
a persistent demo record.

One Vercel project serves the compiled React/Vite frontend and FastAPI through
same-origin `/api` routes using Vercel Services (beta). FastAPI uses SQLAlchemy
and a private pooled `DATABASE_URL` to connect to Neon PostgreSQL with SSL.
Credentials stay in server-side environment settings, never frontend variables.
The owner reports Alembic revision `20261025_06` and catalogue seed verification
passed. Hosted requests/builds do not run migrations; operator migrations use
a separate direct connection. Docker Compose remains the local alternative.

### Reviewer walkthrough

1. Open the demo and confirm eight catalogue products load. Open Small and Big
   Be Seen details: English `Be` should be left of Arabic `س`; neither is editable.
2. Choose the personalized Arabic rectangular tag, enter `سلام`, choose Amiri,
   and inspect the RTL illustrative preview. Latin-only text should be rejected.
3. Check the server-calculated GBP quote: one rectangular tag is £12.00.
   Optionally inspect a letter-only tag at quantity two for the £8.50 pair offer.
   Prices are demonstrations, not a payment request.
4. To test ordering, submit once with a unique synthetic name and an
   `@example.invalid` contact. Confirm the returned order-request number. Do not
   enter real contact details or retry blindly if the response is interrupted.
   There is no payment step, customer account, or public order-history endpoint.
5. Inspect [API health](https://arabic-apparel-and-stickers.vercel.app/api/health),
   [database health](https://arabic-apparel-and-stickers.vercel.app/api/health/db)
   and the [catalogue API](https://arabic-apparel-and-stickers.vercel.app/api/products).
   Independent later retrieval of an order requires an authorized operator's
   narrowly scoped database check; never publish customer rows or credentials.

Deployment evidence: [Issue #4](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/4)
and the [task tracker](docs/TASK_TRACKER.md). Latest reviewed application commit:
[`690f99e`](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/commit/690f99ec35e964c80c2e78315678c1a964a52369);
[CI run](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/actions/runs/40412574765)
passed all six jobs. Vercel reported that commit deployed successfully; the
production alias-to-SHA mapping has not been independently inspected.

Small and Big Be Seen tags share a fixed design: English `Be` on the left and
Arabic `س` on the right. Isolated script spans keep this order in cards, previews,
order summaries and confirmations; customers cannot edit the design.

## Requirements

- Docker Desktop with Docker Compose v2
- Git

## Start locally

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Open the frontend at `http://localhost:5173`. The API is at `http://localhost:8000`.

Stop the stack without removing its database:

```powershell
docker compose down
```

PostgreSQL data persists in the `postgres-data` Docker volume. Do not run `docker compose down -v` unless you deliberately want to remove local data.

## Environment variables

Copy `.env.example` to `.env` and set:

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: PostgreSQL credentials and database name.
- `VITE_API_BASE_URL`: browser-visible FastAPI base URL. Keep `http://localhost:8000` for the default Compose ports.

## Catalogue and prices

All prices are stored as integer pence in PostgreSQL and returned as GBP in the UI.

| Product | Price | Offer |
| --- | ---: | --- |
| Small Be Seen tag | £5.00 | Fixed `Be س` design |
| Big Be Seen tag | £10.00 | - |
| Personalized Arabic rectangular tag | £12.00 | Long names, up to 24 graphemes |
| Small Arabic letter-only tag | £5.00 | Two for £8.50 |
| Personalized Arabic HTV sticker, 5 x 5 inches | £5.00 | - |
| Personalized Arabic HTV sticker, 9 x 4 inches | £9.00 | - |
| Personalized Arabic HTV sticker, 12 x 3 inches | £12.00 | - |
| Be Seen boys' sweater | £15.00 | Two for £25.00 |
| Be Seen men's sweater | £30.00 | Two for £50.00 |
| Be Seen black canvas bag | £20.00 | - |

For eligible products, every complete pair receives the offer price; an odd remaining item uses its standard price. The backend always calculates the final price and does not accept a client-provided price.

HTV stickers support these colours: Black, White, Yellow, Light Blue, Red, Grass Green, Pink, Royal Blue, Purple, Brown, Lake Blue, Rose Gold, Dark Yellow, Rose Red, Aqua Blue, Dark Green, Green, Gold, Silver, and Orange.

Personalized Arabic text is normalized to Unicode NFC and limited to 24 graphemes. It accepts Arabic letters, diacritics, spaces, hyphens, Arabic digits, and Western digits, and must include an Arabic letter. The letter-only tag accepts exactly one Arabic letter, with optional diacritics. Supported fonts are Amiri, Cairo, and Tajawal. Previews are illustrative, not production-accurate.

## Order requests

The UI can submit a demo order request after a valid quote. `POST /api/orders` stores the selected product, validated options, quantity, server-calculated total, customer name, and email or phone in PostgreSQL with status `new`. This is for admin review only; checkout, payment, and authentication are out of scope.

## Database migrations

The local development Compose backend runs Alembic migrations at startup.
Vercel does not: hosted migrations are a separate operator action described in
the [Neon/Vercel runbook](docs/NEON_VERCEL.md). For local Docker only:

```powershell
docker compose exec backend alembic upgrade head
docker compose exec backend alembic current
```

Migrations create and seed products, prices, order requests, the fixed Be Seen display, and the HTV colour palette.

## Verification and tests

```powershell
docker compose exec backend pytest
docker compose exec frontend npm test
docker compose exec frontend npm run build
```

Health endpoints:

- `GET /health`: FastAPI process health.
- `GET /health/db`: SQLAlchemy PostgreSQL connectivity.
- `GET /api/products`: current catalogue and product prices.

## CI/CD

Optional [local observability](docs/OBSERVABILITY.md) instruments catalogue,
pricing and demo orders with sanitized OpenTelemetry signals and a separate
Grafana LGTM stack. This does not enable Vercel production monitoring; see the
tracker for actual ingestion, exemplar and UI verification results. The
[dashboard and log-to-trace screenshots](docs/OBSERVABILITY.md#owner-provided-ui-evidence)
record owner-verified local UI evidence, not independent review.

[Neon and Vercel preparation](docs/NEON_VERCEL.md) documents the pooled runtime
URL, separate direct migration URL, SSL settings and Vercel project setup. The
migration helper defaults to connection-free validation. Neon is connected to
the live application; historical preparation-only checks did not connect to it.

The [frontend dependency security review](docs/DEPENDENCY_SECURITY.md) records
remediation of the six npm audit findings: full and production-only audits now
report zero for the rebuilt frontend. Vitest was upgraded explicitly to 4.1.12;
tests and production build pass. The current development-server Docker image
is for local hot reload. [Production deployment preparation](docs/PRODUCTION_DEPLOYMENT.md)
provides separate Nginx/static and non-reloading API images, private PostgreSQL,
required environment settings and an isolated browser smoke-test command.

[CI/CD setup and rollback](docs/CI_CD.md) documents the workflows and local
isolated validation commands. CI checks backend tests, Alembic-migrated
PostgreSQL integration, frontend tests/production build using `npm ci`, and both
development Docker image builds on pull requests and pushes to `main`. The
production-smoke job also builds production images and checks the real browser
journey; actual published run results are recorded in Issue #5.

Separate development and production deployment workflows are prepared, but
disabled by explicit publication holds until real hosting, credentials and
production environment approval rules are configured and a reviewed code change
removes the holds. The live Vercel Git integration operates separately from these
held GitHub deployment jobs; a hosted rollback drill has not been demonstrated.
See [Issue #5](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/5)
and the [implementation evidence](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/5#issuecomment-6422151090)
for actual results and blockers.

## AI-assisted development

Vercel Hobby preparation uses one repository-root project with Vite/FastAPI
Services (beta), same-origin `/api` and `/api/health` endpoints. Follow the
[exact import settings and release gates](docs/NEON_VERCEL.md). The owner reports
Neon revision `20261025_06` and seed verification succeeded. The public demo is
live; Hobby is suitable only for a personal, non-commercial demo.

Remaining Zoomcamp grading work is tracked in the
[public GitHub Issues tracker](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues).
Each issue includes priority, acceptance criteria and required evidence:

- [#1: Agent use of the tracker](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/1)
- [#2: PostgreSQL integration tests and one test command](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/2)
- [#3: Full-stack reproducibility evidence](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/3)
- [#4: Public deployment](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/4)
- [#5: CI/CD and rollback](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/5)
- [#6: Correlated telemetry](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/6)
- [#7: User-impact alert](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/7)
- [#8: On-call responder agent](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/8)
- [#9: Grading evidence and independent review](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/9)

These issues describe remaining work; they do not claim implemented capabilities.

Project instructions for coding agents are in [AGENTS.md](AGENTS.md). The
[AI agent workflow](docs/AI_AGENT_WORKFLOW.md) distinguishes documented Codex
use from proposed collaboration roles, and the
[task tracker](docs/TASK_TRACKER.md) records task status and evidence. See
[spec.md](spec.md) for product acceptance criteria and
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for application architecture.
