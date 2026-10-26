# CI/CD and rollback

Implementation for [Issue #5](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/5).
No hosting provider, deployment URL or credentials are configured by this change.
CI is implemented for publication. Deployment workflows are preparation only:
both jobs have an explicit `false &&` publication hold in addition to enable
variables. They cannot deploy from this publication, including manual dispatch.

## Checks and triggers

| Workflow | Trigger | Work |
| --- | --- | --- |
| [CI](../.github/workflows/ci.yml) | Every pull request; push to main | Backend pytest, PostgreSQL integration, frontend tests/build using Node 22 and npm ci, both Docker image builds |
| [Development](../.github/workflows/deploy-development.yml) | Successful CI workflow_run for a main push in this repository | Currently held; future automatic deployment requires reviewed hold removal and DEVELOPMENT_DEPLOY_ENABLED=true |
| [Production](../.github/workflows/deploy-production.yml) | Manual workflow_dispatch on main with full release_sha | Currently held; future release/rollback requires reviewed hold removal, PRODUCTION_DEPLOY_ENABLED=true and production required-reviewer protection |

CI uses contents: read only, no deployment credentials and no image push.
The production-smoke job builds separate production images and exercises an
isolated browser-to-Nginx-to-API-to-PostgreSQL stack automatically on PRs/main
pushes. Actual run results are recorded in Issue #5, separately from held hosted
deployment work. See [production deployment](PRODUCTION_DEPLOYMENT.md).
The backend job also runs `bash scripts/test-deploy.sh` with fake GitHub/curl
tools to check guard failures, async-response rejection and release/rollback
requests without network calls. This is client validation, not a hosting drill.
Deployment adds actions: read to verify successful CI for the exact requested SHA.
Checkout does not persist credentials. No pull_request_target, PR artifacts or
fork code are consumed by deployment. Deployments serialize per environment and
do not cancel an in-progress release. Disabled deployment jobs are skipped; a
green CI run or skipped deployment is not evidence of a deployed application.

The integration job uses an ephemeral PostgreSQL 16 service named apparel_ci.
The visible CI-only database password is a disposable test value, never a hosting
credential. Alembic upgrades an empty database before tests; tests check migration
head, seeded catalogue, invalid text, pair pricing, real order persistence and
database health with no dependency overrides. Existing SQLite tests remain.

## Reproduce locally

Run from the repository root with Docker Desktop available:

```powershell
docker compose -p apparel-ci-check -f compose.ci.yml build
docker compose -p apparel-ci-check -f compose.ci.yml run --rm backend
docker compose -p apparel-ci-check -f compose.ci.yml run --rm --no-deps frontend
docker compose -p apparel-ci-check -f compose.ci.yml down
```

Use a distinct unused project name. This stack has no published ports and uses
tmpfs for PostgreSQL; it does not use .env values or mount the developer database.
Do not add --env-file or use docker compose down -v. The backend test skips in
ordinary pytest unless RUN_POSTGRES_INTEGRATION=1; opt in only against a dedicated
apparel_ci database that has been migrated. Commands above build current sources,
not an old running application image. Neither command contacts a hosting provider.

## Hosting setup required before enabling CD

1. Select hosting and implement a trusted HTTPS adapter accepting POST JSON
   containing sha (full commit SHA) and environment (development or production).
   [scripts/deploy.sh](../scripts/deploy.sh) is the client contract, not a
   provider-specific deployment implementation. A generic provider deploy hook
   is insufficient unless it honors the exact SHA and synchronous result contract.
2. The adapter must authenticate the bearer token, allow only the intended
   repository/environment, serialize releases, fetch exactly the tested revision,
   build immutable release images, and record previous/current image digests,
   commit SHAs and Alembic revision. Keep environment databases separate and
   persistent, with backups. Configure actual browser API URL, HTTPS, and CORS.
   Development Dockerfiles intentionally retain Vite/Uvicorn reload. Use the
   new production Dockerfiles and standalone production Compose configuration;
   local production serving is prepared, actual hosted configuration is pending.
3. Adapter runs migrations once per release, deploys both services, verifies
   /health, /health/db, catalogue and browser-to-API quote behavior, and returns
   HTTP 200/204 ONLY after successful readiness checks. An async 202 response must not be
   treated as successful rollout; use an adapter that waits for completion.
   On timeout, inspect hosting state before retrying; do not deploy twice blindly.
4. Create GitHub environments development and production. Restrict deployments
   to main. For production configure required reviewers, prevent self-review and
   disable administrator bypass; workflow_dispatch alone is not approval.
   These settings cannot be declared by these workflow YAML files.
5. In EACH environment set secret names DEPLOY_WEBHOOK_URL and
   DEPLOY_WEBHOOK_TOKEN to real adapter credentials. Set provider database and
   other credentials in the hosting secret store, never Git or workflow output.
   The workflows suppress adapter responses/errors and never enable shell xtrace.
6. Obtain owner approval to deploy and submit a reviewed change removing the
   explicit `false &&` hold in both deployment job conditions only after verifying
   hosting and required-reviewer setup. Then set repository variables
   DEVELOPMENT_DEPLOY_ENABLED and PRODUCTION_DEPLOY_ENABLED to true only after
   their setup is ready. Leave them unset/false for this task. Successful main
   CI then triggers development automatically; production is manually dispatched
   and waits for configured environment approval. Require CI jobs in branch rules.

GitHub references: [workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows),
[environment protection](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments).

## Rollback strategy (not yet exercised against hosting)

Before each release retain the last healthy SHA/digests, migration revision and
verified database backup. Prefer backward-compatible expand/contract migrations.
For an application-only regression, freeze automatic dev delivery by setting
DEVELOPMENT_DEPLOY_ENABLED=false, select the last healthy SHA with successful
main CI, and redeploy the retained images through the adapter. Production uses
the same manual workflow with that SHA and required approval. Development
rollback currently requires the hosting operator's adapter/tooling; there is no
manual development workflow trigger. Verify endpoints, browser quoting and data
integrity; record timestamps, versions, command results and reviewer findings.

Do not run Alembic downgrade blindly. If the old application cannot use the new
schema, stop and approve a forward repair or backup restore procedure separately;
preserve orders and never reset the shared database. Test this path in isolated
development with synthetic data before enabling production. No rollback success
is claimed until that exercise is recorded in Issue #5.

## Grading status

The [official rubric](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp/blob/main/project/README.md)
was read on 2026-10-26. CI/CD maximum credit requires tests, automatic dev deploy
and manual production deploy. These files prepare that path but do not yet meet
the full criterion: hosting adapter, protected environment setup, actual
deployment and hosted rollback evidence remain pending. CI run results are
recorded in Issue #5 after publication; a main push run does not demonstrate a
PR-triggered run. Independent review is also outstanding.

## Local evidence - 2026-10-26

- Both images built with `docker compose -p apparel-ci-check -f compose.ci.yml build`.
- Isolated backend run applied all six migrations to `20261025_06` head and
  passed all 29 tests, including the real PostgreSQL integration test.
- Isolated frontend run completed `npm ci`, all five tests and production build.
- `actionlint` validated all three workflow files; deployment script `bash -n`
  and rejection of invalid SHA/missing hosting configuration passed.
- `scripts/test-deploy.sh` passed all mocked guard/release/rollback checks;
  no real provider was called. All 13 local Markdown links resolved, and
  changed-file credential-pattern/whitespace checks passed.
- npm reported six vulnerabilities: three moderate, one high and two critical.
  Dependency upgrades were not applied in this CI/CD task. Pytest emitted a
  Starlette/AnyIO deprecation warning; no test failures occurred.
- Subsequent [dependency remediation](DEPENDENCY_SECURITY.md) resolved those six
  npm findings in the updated frontend manifests/image. The earlier results
  above are retained as historical CI/CD implementation evidence.
- The isolated stack was stopped with `down` (no volume deletion). No developer
  database was migrated or reset and no hosted deployment was attempted.
