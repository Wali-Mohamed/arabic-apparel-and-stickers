# Production deployment preparation

This implements local production-style preparation for Issues #4 and #5.
No public deployment, purchase, secret change, approval-setting change or hosted
rollback has occurred. Deployment workflow publication holds remain in place.

## Runtime architecture

```text
Browser -> HTTPS edge (host TLS proxy or managed load balancer)
        -> loopback:8080 Nginx (static Vite dist + /api reverse proxy)
        -> private FastAPI:8000 -> private PostgreSQL:5432
```

`compose.production.yml` is standalone: do not merge it with development
`compose.yml`, which intentionally exposes local development ports and mounts
source for Vite/Uvicorn hot reload. Development Dockerfiles remain unchanged.

- `frontend/Dockerfile.production` uses Node 22, committed lock and npm ci to
  build Vite, then copies dist only into an unprivileged Nginx image. Node,
  source and node_modules are absent from its final runtime image. The empty
  VITE_API_BASE_URL uses same-origin `/api`; the existing default localhost API
  remains for development. This is static production serving, not Vite preview.
- Nginx proxies `/api/`, `/health` and `/health/db` without stripping prefixes.
  Docker DNS re-resolves the backend on replacement. Host is preserved for
  FastAPI validation; forwarding headers are replaced, not appended. Uvicorn
  intentionally ignores forwarded headers. HTTPS redirection, certificates and
  HSTS belong to the trusted edge. Production slash redirects/docs are disabled,
  so API responses do not generate internal HTTP redirect URLs behind TLS.
- Backend production image runs as UID 10001, two Uvicorn workers without
  reload. A separate one-shot migration container reaches Alembic head before
  the API starts; migrations are not executed by every worker. Rerun the migration
  service for every release before replacing API workers. No migration rewritten.
- API and database have no published ports; PostgreSQL joins only an internal
  data network. Frontend is loopback-bound by default. A separate named
  production-postgres-data volume is scoped to the Compose project.
- Frontend/backend/migration use read-only filesystems, tmpfs scratch space,
  dropped capabilities and no-new-privileges. PostgreSQL retains its standard
  entrypoint permissions for initialization and durable data writes.

## Configuration and first start (only after separate hosting approval)

Copy `.env.production.example` to an ignored `.env.production` outside public
artifacts or inject variables through the host's secret store. Never use the
development .env defaults. Required inputs:

| Variable | Purpose |
| --- | --- |
| POSTGRES_PASSWORD | Strong unique password; required, no production fallback |
| POSTGRES_DB / POSTGRES_USER | Database/name of initial account; defaults apparel |
| PUBLIC_ORIGIN | Exact HTTPS origin including nonstandard port if applicable; no path/credentials/wildcard |
| ALLOWED_HOSTS | Comma-separated actual hostnames, no schemes/ports/wildcards; include 127.0.0.1 for container health |
| FRONTEND_BIND_ADDRESS / FRONTEND_PORT | Default 127.0.0.1:8080 behind a host TLS proxy |
| RELEASE_TAG | Release-specific local image tag; use immutable tags/digests in the future hosting adapter |

For example-domain placeholders see the example file; no actual public URL is
invented. Database credentials are runtime environment values, not build args.
The API constructs/escapes the SQLAlchemy URL from components; DATABASE_URL is
also supported for a managed database outside this Compose stack. Use a TLS
database URL for remote managed PostgreSQL. Never print `docker compose config`
or container environment inspection in shared logs: resolved values include secrets.

After authorization on the chosen host, prepare DNS and a TLS edge forwarding
to 127.0.0.1:8080, allow only 80/443 publicly and restrict SSH to administrators.
Keep 5432/8000/8080 blocked externally. A host TLS proxy can reach loopback;
a containerized edge needs its own explicitly designed private network instead.
Do not simply bind all interfaces and claim HTTPS exists.

```powershell
# Planned host commands, not evidence of public deployment:
docker compose --env-file .env.production -p apparel-production -f compose.production.yml build
docker compose --env-file .env.production -p apparel-production -f compose.production.yml up --no-deps --force-recreate migrate
docker compose --env-file .env.production -p apparel-production -f compose.production.yml up -d --wait
```

On a first start use `up -d --wait postgres` before the explicit migration
command. Do not copy developer PostgreSQL data into hosting. Database initial
user currently owns migrations; before handling real customer data, split
migration ownership from a least-privilege API login and provision backups.
Environment secrets are visible to Docker administrators: use host access controls
and a provider secret store. No secrets are baked into the frontend bundle.

## Origin, headers and abuse boundaries

Production startup requires explicit trusted hosts and PUBLIC_ORIGIN. Public
origins must be HTTPS; HTTP is allowed only for explicit localhost/127.0.0.1 or
the internal frontend hostname used by isolated smoke tests. CORS permits only
that origin and GET/POST with Content-Type. Foreign browser Origin headers on
write methods are rejected, even where CORS would only hide a response.
Clients without Origin remain allowed: this unauthenticated demo endpoint is
not protected by authentication, and Origin checks are not bot protection.

Nginx applies request/body/time limits and a per-connection-IP request limit
(10/s with burst 40). Behind a host edge it sees the proxy IP, so the limit is
aggregate until trusted real-client-IP handling is deliberately configured.
Never trust arbitrary internet X-Forwarded-For. Add provider edge rate/abuse
controls before collecting real contacts. CSP restricts scripts and connections
to self; Google Fonts remain explicitly allowed, with inline styles permitted
for the existing live Arabic colour/font preview. Fonts may require third-party
privacy review/self-hosting before real customer use.

Nginx access logs omit query strings and request bodies; Uvicorn access logs are
disabled and SQLAlchemy hides query parameters in exceptions. Backend errors
still need an operator retention/access policy. No public order-list endpoint or
customer records are introduced. No payment/authentication functionality added.

## Local smoke tests and CI

Run from the repository root with Docker Compose supporting `!reset` and Git
Bash/Linux bash available:

```bash
bash scripts/test-production.sh
```

The script generates an isolated project name, uses a known disposable test
password and tmpfs database override, and publishes **no host ports**. It builds
production frontend/backend plus a locked Playwright browser test image. It
tests real UI browsing of eight products, rejects Latin personalization, renders
RTL Arabic and colour changes, quotes HTV and pair prices, submits synthetic HTV
and fixed-tag orders, and verifies persistence using a separate database session.
It also checks forbidden host/origin, security headers, real DB health and no
Vite development client, then checks persistence/proxy health after API restart.
The exit trap uses plain down; it never deletes existing database volumes.
Runtime inspection asserts no host port bindings and no persistent database
mounts. The synthetic password deliberately includes URL-special characters
to verify safe SQLAlchemy URL construction and Alembic percent escaping.
Do not apply the smoke override to a live production database.

The production-smoke CI job performs this same isolated test automatically on
pull requests and main pushes. Existing backend, frontend, integration and dev
image checks remain. Actual run URLs and conclusions are recorded in Issue #5
after publication; these CI checks never deploy to a hosted environment.

For manual local browsing without publicly serving it, set PUBLIC_ORIGIN to
http://localhost:8080 and ALLOWED_HOSTS to localhost,127.0.0.1 in a separate
ignored local env, use a unique Compose project and the production file only.
This retains its own data volume. The automated browser tests use the internal
http://frontend:8080 origin instead. Do not use synthetic test credentials outside
the disposable test stack.

## Hosting choices and estimated budget

Recommendation for this low-traffic capstone: one small VPS with Docker Compose,
host TLS proxy, Nginx/static assets, private API and PostgreSQL, plus off-host
encrypted backups. Start with 2 vCPU/4 GiB RAM and 40-80 GiB SSD; 1 vCPU/2 GiB
can be trialled with images built in CI, but leaves less headroom. Size estimates
are engineering starting points, not benchmarked capacity. Monitor disk, memory,
DB connections and latency before raising limits; browser test images are CI-only
and should not be installed on the small production host.

| Option | Budget and tradeoff |
| --- | --- |
| DigitalOcean VPS | Official Basic prices checked 2026-10-26: 1 vCPU/2 GiB/50 GiB $12/month; 2 vCPU/4 GiB/80 GiB $24/month. Budget roughly $30-45/month total for the recommended size with backup/domain/tax allowance; total is an estimate, not a quote. Owner operates OS, TLS and database backups. |
| Managed platform such as Render | Separate web/private services and managed PostgreSQL reduce OS/DB work; budget an estimated $25-60+/month for a small paid arrangement, verify actual region/resources/storage quote before purchase. This Compose setup is not a Render blueprint: configure private discovery, health checks, build/deploy commands, secrets and same-origin routing for that platform. |

Sources: [DigitalOcean official pricing](https://www.digitalocean.com/pricing/droplets),
[Render official pricing](https://render.com/pricing),
[Render compute plans](https://render.com/docs/compute-plans).
Budget estimates exclude traffic spikes and support; domain, taxes, backups,
storage and separate development environments can increase costs. No free-tier
database should be assumed durable or appropriate for customer contacts.

## Releases, rollback and remaining gates

Retain previous healthy image digests, schema revision, configuration and a
restorable backup. Run additive migrations once, replace API/static images,
verify health and synthetic journey, then record the release. Roll back the
application images only when schema compatibility is confirmed. Do not blindly
downgrade Alembic or restore over orders. Test restore/rollback in a separate
environment and obtain approval for any destructive repair.

Existing scripts/deploy.sh remains a generic HTTPS adapter client; implement
and test a real provider adapter with exact-SHA deployment, migration/smoke checks
and synchronous completion before wiring it up. Development/production jobs
retain explicit false publication holds. Hosting selection, actual DNS/TLS,
secret storage, protected production reviewers, separate deployment authorization,
public URL evidence, hosted rollback drill and independent review are still
pending. See [CI/CD runbook](CI_CD.md). Neither Issue #4 nor #5 is complete.

## Verification observed locally - 2026-10-26

- Development/test images built; isolated Alembic/PostgreSQL suite passed 31
  backend tests, including production security settings. Existing Starlette/AnyIO
  deprecation warning remains, with no backend failures.
- Frontend npm ci, six tests and production build passed; production-only audit
  returned zero. Production Vite static build and both production runtime image
  builds passed. Nginx configuration validation and absence of Node in the
  final static image were verified.
- Final backend image explicitly defaults APP_ENV to production and rejected
  startup without database credentials in a separate fail-closed check.
- Final `bash scripts/test-production.sh` passed both Playwright tests, runtime
  no-port/no-persistent-mount assertions, two synthetic order persistence checks
  and proxy/DB health after API restart. Its special-character database password
  also verified URL encoding through Alembic. Cleanup completed with plain down.
- Workflow actionlint passed. The first browser attempt failed due to an overly
  exact Font selector, which was corrected before the passing runs. No public
  endpoint, TLS certificate or hosted rollback was verified.
