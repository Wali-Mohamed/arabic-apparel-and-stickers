# Project Task Tracker

This is the repository-local record of scoped work and evidence. The
[public GitHub Issues tracker](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues)
tracks the remaining grading work. Issue creation does not complete implementation.

| ID | Task | Status | Acceptance criteria | Supporting evidence |
| --- | --- | --- | --- | --- |
| CAP-01 | Define product specification and architecture | Complete | Current scope, API flows, persistence, and acceptance criteria are documented | `spec.md`, `docs/ARCHITECTURE.md`, commit `c4eb335` |
| CAP-02 | Provide a reproducible Compose setup | Complete | Fresh isolated PostgreSQL migration reaches head; services start; health and catalogue APIs respond | Alembic `20261025_01`-`20261025_06`; isolated verification was performed locally on 2026-10-26, but its command transcript is not committed |
| CAP-03 | Protect HTV migration compatibility | Complete | PostgreSQL JSON/JSONB migration reaches head on an empty database | `backend/alembic/versions/20261025_06_update_htv_colours.py`; isolated local verification was performed on 2026-10-26 |
| CAP-04 | Document AI-assisted development context | Complete | Agent instructions, role boundaries, collaboration protocol, and real-versus-proposed workflow are documented | `AGENTS.md`, `docs/AI_AGENT_WORKFLOW.md` |
| CAP-05 | Public tracker and demonstrated agent use | In progress; independent review pending | Public tracker is linked; actual agent handoff and independent review demonstrate use | [Issue #1](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/1); [actual Codex review](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/1#issuecomment-6421542642) documents agent interaction; documentation publication authorized below; issue remains open |
| CAP-06 | Public deployment evidence | Production configuration implemented; hosting/approval pending | Repeatable deployment, public URL/demo, persistence and rollback evidence | [#4](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/4); [production runbook](PRODUCTION_DEPLOYMENT.md); no public deployment performed |
| CAP-07 | PostgreSQL integration tests and single test command | Partially implemented under CAP-09, P1 | Unit/frontend and real PostgreSQL integration tests pass through one command | [#2](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/2); real PostgreSQL integration added with CI; combined single-command runner and broader coverage still pending; existing SQLite/UI mock tests retained |
| CAP-08 | Full-stack reproducibility evidence | Planned, P1 | Isolated Compose startup, migrations, browser flow and restart persistence are recorded | [#3](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/3); supplements CAP-02/03 evidence |
| CAP-09 | CI/CD and rollback | In progress; CI implemented, deployment and independent review pending, P1 | PR checks, automatic dev deploy, manual production gate and rollback evidence | [#5](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/5) records actual publication/Actions results; [CI/CD setup and evidence](CI_CD.md); deployment jobs held, no hosted deployments |
| CAP-10 | Correlated telemetry | Planned, P2 | Metrics, traces and structured logs share trace IDs and are viewable without customer data | [#6](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/6) |
| CAP-11 | User-impact alert | Planned, P2 | Reversible isolated fault demonstrates firing and recovery | [#7](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/7); depends on CAP-10 |
| CAP-12 | Bounded on-call agent | Planned, P2 | Alert triggers agent diagnosis/remediation and demonstrated recovery | [#8](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/8); depends on CAP-11 |
| CAP-13 | Grading evidence and independent review | Planned, P1 | All current criteria mapped to verified evidence; remaining gaps and submission obligations recorded | [#9](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/9) |

## Grading baseline

The [official project rubric](https://github.com/DataTalksClub/ai-dev-tools-zoomcamp/blob/main/project/README.md),
checked on 2026-10-26, contains 12 criteria worth 24 points with 10 required to
pass. The backlog targets remaining evidence and maximum-credit capabilities;
every issue is not a mandatory passing prerequisite. Priorities: P1 covers core
delivery and evidence; P2 covers advanced operations capabilities. Recheck the
rubric and live course platform before submission; three peer reviews are also
required. Existing CAP-01 through CAP-04 records are preserved, not newly verified.

## Tracker creation handoff — 2026-10-26

- Task: CAP-05; owner/role: Codex, implementer under user direction.
- Scope: inspect sources and existing issues, publish a nonduplicated grading
  backlog with priorities, acceptance criteria and evidence requirements, and
  link it locally. No application implementation, commit or push was requested.
- Acceptance: repository is public with Issues enabled; existing issues checked
  across all states; remaining grading work has public issue URLs and local links.
- Files changed: `README.md`, `docs/TASK_TRACKER.md`,
  `docs/AI_AGENT_WORKFLOW.md`. Preserved pre-existing README edits and untracked docs.
- Commands/results: `git status --short`; source reads and `rg --files` / `rg -n`;
  `git diff -- README.md`; `gh repo view ... --json url,visibility,hasIssuesEnabled`
  confirmed PUBLIC and Issues enabled; `gh issue list --state all --limit 300`
  returned no issues; `gh api` read the official project rubric;
  `gh issue create --body-file` created issues #1–#9. GitHub CLI required network
  escalation after the initial sandbox connection failure.
- Verification: final GitHub issue listing and local diff/whitespace review;
  no application tests run for this documentation/backlog task.
- Reviewer findings: independent review has not occurred; CAP-05 remains open.
- Risks/blockers: public issues reference local documentation not yet committed
  or pushed; grading rules can change; deployment and CI/CD need separate explicit
  approval. No secrets or customer records were included in issue bodies.
- Next owner: independent reviewer validates issue coverage and links; owner
  authorizes any later commit/push. Continue implementation through the linked issues.

## Actual Issue #1 review handoff - 2026-10-26

- Task: CAP-05, [Issue #1](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/1).
- Owner/role: OpenAI Codex, user-directed evidence reviewer. This is the same
  agent that created the tracker; this review does not satisfy independent review.
- Scope and acceptance: read the live issue and requested docs; assess actual
  tracker/workflow evidence without changing application functionality; publish
  findings, validate links and whitespace, and close only if all criteria are met.
- Public result: [review comment](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/1#issuecomment-6421542642).
  Tracker links are present locally and this issue-referenced agent review is
  real public interaction. Independent validation and documentation publication
  remain pending, so Issue #1 is left open.
- Files changed in this task: `docs/TASK_TRACKER.md` only. Existing README edits,
  AGENTS.md and workflow documentation were preserved.
- Commands/results: read Issue #1 with `gh issue view --json`; inspected the six
  required/context docs; ran `git status --short`, `git diff -- README.md`, and
  `git ls-files -- README.md AGENTS.md docs/TASK_TRACKER.md docs/AI_AGENT_WORKFLOW.md`.
  Only README is tracked among these four; the other three are untracked.
  A PowerShell Markdown-link check resolved all five relative links in the four
  requested docs. `gh repo view` confirmed PUBLIC/Issues enabled; `gh issue list`
  verified #1-#9; `gh api` confirmed the official rubric path exists and published
  docs contains only ARCHITECTURE.md, with no root AGENTS.md. Posted the review
  using `gh issue comment 1 --body-file`. `git diff --check` passed before posting.
- Final verification: relative-link validation passed again (five links);
  GitHub API confirmed the returned comment URL and Issue #1 remained OPEN.
  `git diff --check` passed, as did an explicit trailing-whitespace and conflict-marker
  check on this untracked file. Git warned about README line endings only.
- Reviewer findings: documentation distinguishes proposed roles from executed
  work and includes an evidence policy and handoff. Historical CAP-01-CAP-04
  completion claims were not reverified; #3/#9 track missing reproducibility and
  final review evidence. No tests/builds were run for this documentation review.
- Risks/blockers: local agent/workflow/tracker documents are not published; this
  review is not independent from the implementer. No commit or push was made.
- Next owner: independent reviewer assesses the evidence; repository owner
  separately authorizes publication. Do not mark CAP-05 complete yet.

## Documentation publication handoff - 2026-10-26

- Task: CAP-05; owner/role: Codex, implementer under explicit user authorization
  to stage, commit and push only the four agent/tracker documentation files.
- Scope and acceptance: verify documentation against source, preserve the real
  Issue #1 comment and outstanding independent review, check links and sensitive
  content, and publish to origin/main without force-pushing. Do not close Issue #1.
- Files: `AGENTS.md`, `docs/AI_AGENT_WORKFLOW.md`, `docs/TASK_TRACKER.md`, `README.md`.
- Checks observed before publication: initial status contained only these four
  intended files; reviewed docs, specification, architecture, Compose, API routes,
  Arabic validation, pricing, backend startup and frontend package scripts.
  `git fetch origin main` succeeded; GitHub confirmed Issue #1 OPEN, the actual
  review comment, issues #1-#9 and the rubric link.
- Publication procedure: validate local Markdown links and scan the four files
  for sensitive material; review the staged diff and `git diff --cached --check`;
  commit with `docs: publish agent workflow and GitHub task tracker`; push with
  `git push origin main`; verify public file contents and remaining Git status.
  The resulting commit hash and observed push/public-access results are reported
  in the task response, rather than predicting success in this commit.
- Review result: this remains implementer verification, not independent approval.
  Earlier handoffs describe the state at their respective review times; their
  unpublished-file findings are historical once this publication succeeds.
- Remaining risk/next owner: independent reviewer must validate the published
  evidence before CAP-05 can be complete. Historical application test/migration
  claims were not re-executed by this documentation task. No application changes,
  CI/CD changes or deployment are included.

## CI/CD implementation handoff - 2026-10-26

- Task: CAP-09, Issue #5; owner: Codex implementer. User explicitly authorized
  CI/CD configuration and an issue evidence update, but no commit, push or deployment.
- Public handoff: [Issue #5 implementation evidence](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/5#issuecomment-6422151090).
- Acceptance: CI on PR/main push runs backend, frontend, build, Docker validation
  and isolated migrated PostgreSQL integration; separate gated CD workflows,
  real setup prerequisites, minimal permissions and rollback documentation.
- Files: `.github/workflows/ci.yml`, `.github/workflows/deploy-development.yml`,
  `.github/workflows/deploy-production.yml`, `scripts/deploy.sh`,
  `scripts/test-deploy.sh`, `compose.ci.yml`,
  `backend/tests/integration/test_postgres.py`, `backend/.dockerignore`,
  `frontend/.dockerignore`, `docs/CI_CD.md`, `docs/ARCHITECTURE.md`,
  `docs/TASK_TRACKER.md`, `README.md`, `spec.md`.
- Commands/results: read official rubric and Issue #5 via gh; built both images;
  isolated `compose.ci.yml run --rm backend` migrated empty PostgreSQL through
  all six revisions and passed 29 tests; isolated frontend run used npm ci,
  passed five tests and production build. Existing stack checks also passed
  (28 backend tests plus one intentionally skipped integration, five frontend tests).
  actionlint passed all workflow files. bash syntax and missing-config/invalid-SHA
  guards passed. `scripts/test-deploy.sh` passed mocked release/rollback, failed-CI,
  stale-development, missing-config, invalid-SHA and async-response checks without
  hosting access. All 13 local Markdown links resolved; changed-file credential
  pattern and whitespace checks passed. Isolated stack removed with plain down,
  no persistent volumes.
- Findings: npm reported six vulnerabilities (three moderate, one high, two
  critical); dependency remediation remains separate. One Starlette/AnyIO
  deprecation warning. No customer data or hosting credentials used.
- Risks/blockers: workflows remain local; successful GitHub PR checks require
  later authorized publication. No real hosting adapter, deployment credentials,
  approval settings, dev/prod deployment or hosted rollback drill is demonstrated.
  Deploy jobs default to disabled via unset enable variables. Full CI/CD rubric
  credit is not met; Issue #5 remains open. Independent reviewer validation pending.
- Next owner: reviewer validates diff and evidence; owner authorizes eventual
  publication and separately selects/configures hosting and production reviewers.

## Frontend npm security remediation handoff - 2026-10-26

- Task: follow-up to CAP-09 npm audit findings; owner: Codex implementer.
- Scope/acceptance: identify package chains and exposure, apply compatible
  remediation with major-change impact explained first, update both manifests,
  pass clean install/tests/build/Docker checks, review CI/CD credentials and
  permissions. Do not alter PostgreSQL data/volumes, commit, push or deploy.
- Files changed in this task: `frontend/package.json`, `frontend/package-lock.json`,
  `README.md`, `docs/CI_CD.md`, `docs/TASK_TRACKER.md`,
  `docs/DEPENDENCY_SECURITY.md`, and three JSON reports in `docs/security/`.
  All pre-existing CI/CD implementation files/edits were preserved.
- Findings and fix: six dev-tool package entries (Vitest, mocker, tinypool,
  nested Vite, esbuild, vite-node). No patched Vitest 2.x covers the advisories.
  Explained Vitest 4 migration/Node requirements before selecting exact 4.1.12;
  React/Vite/TypeScript/jsdom majors unchanged, no force or transitive overrides.
  npm 10 resolver failed twice without manifest changes; disposable npm 11
  update succeeded and ordinary npm 10 npm ci verified the resulting lock.
- Commands/results: baseline `docker compose exec -T frontend npm audit --json`
  found six (three moderate, one high, two critical); omit-dev audit found zero.
  `docker build --tag apparel-frontend-audit:verified ./frontend` passed; fresh
  `docker run --rm` (no mounted volumes) ran npm ci, five passing frontend tests,
  production build, npm ls and both audits. Full and omit-dev audits now zero.
  Workflow actionlint passed; manual review found only contents: read and
  deployment actions: read, environment-scoped secret references, no secret
  printing or credential literals. Fake CI/test credentials identified as such.
- Evidence: [security assessment and raw audits](DEPENDENCY_SECURITY.md).
- Risks/reviewer findings: implementer checks only; independent review remains
  outstanding. Existing running frontend still uses old node_modules because no
  existing volumes were modified. Rebuild/dependency refresh required before
  using this fix there. No hosted image was inspected or deployed. Current Vite
  dev-server Dockerfile is not approved for public production serving; zero npm
  findings does not cover backend, OS images or all application security risks.
- Next owner: independent reviewer validates the dependency change; owner
  separately authorizes eventual publication/runtime refresh and hosting setup.

## CI/CD and security publication handoff - 2026-10-26

- Task: CAP-09; owner: Codex implementer. User authorized reviewing, validating,
  committing all task files with `ci: add automated validation and dependency
  security fixes`, and pushing origin/main normally. Hosted deployment remains
  prohibited; Issue #5 must stay open until its acceptance criteria are met.
- Scope/files: publish all pending CI workflows, deployment client/mock checks,
  isolated PostgreSQL integration test and Compose file, Docker ignore rules,
  frontend manifests, dependency security assessment/raw audits, README/spec,
  architecture, CI/CD and tracker documentation. No application behavior change.
- Review: contents: read only in CI; deployment adds actions: read. No secrets
  found in inspected files/credential-pattern scan; test database credentials
  are explicitly ephemeral. npm changes remove the six audited tool findings.
  Existing audit snapshots and historical unpublished-file handoffs are retained.
- Safety finding: GitHub API showed no repository deployment enable variables
  and no deployment environments. Added explicit `false &&` publication holds
  to both deployment jobs; changing variables alone cannot enable them. Holds
  require a reviewed change after hosting/reviewer setup and owner authorization.
- Checks: rebuilt both Docker images; isolated empty tmpfs PostgreSQL reached
  Alembic `20261025_06` head and passed all 29 backend tests. Frontend clean npm ci,
  five tests and production build passed after Vitest 4.1.12; full/production-only
  audits both returned zero. actionlint and mocked deployment
  script checks passed. Relative documentation links and whitespace checks passed.
- Publication/run evidence: record the resulting commit, actual job conclusions
  and run URLs in Issue #5 and the task response after pushing; do not predict
  future Actions results in this commit. No production workflow is dispatched.
- Remaining gaps: actual hosted dev/prod deployment, adapter/credentials,
  production serving and protected environment configuration, real rollback drill,
  PR-triggered run evidence and independent review. Vite dev server is not
  production-ready. No existing database volumes are deleted/reset.
- Next owner: reviewer assesses implementation and Actions evidence; owner
  separately authorizes hosting configuration and deployment hold removal.

## Production deployment preparation handoff - 2026-10-26

- Task: CAP-06/CAP-09, Issues #4/#5; owner: Codex implementer. User authorized
  production code/configuration, local tests, hosting research and issue comments;
  no public deployment, purchase, secret/settings changes, commit or push.
- Acceptance: separate static production frontend and non-reloading API;
  development hot reload retained; same-origin API routing, private PostgreSQL,
  explicit production credentials/host/origin checks, health and migration gates;
  production build/browser/persistence smoke tests and deployment/cost runbook.
- Files changed: `.github/workflows/ci.yml`, `.gitignore`,
  `.env.production.example`, `backend/Dockerfile.production`,
  `backend/app/main.py`, `backend/app/database.py`, `backend/alembic/env.py`,
  `backend/tests/test_production_settings.py`, `frontend/Dockerfile.production`,
  `frontend/nginx.production.conf`, `frontend/src/App.tsx`,
  `frontend/src/App.test.tsx`, `compose.production.yml`,
  `compose.production-smoke.yml`, `scripts/test-production.sh`,
  `tests/production/{Dockerfile,.dockerignore,package.json,package-lock.json,production.spec.js}`,
  `README.md`, `spec.md`, `docs/ARCHITECTURE.md`, `docs/CI_CD.md`,
  `docs/DEPENDENCY_SECURITY.md`, `docs/PRODUCTION_DEPLOYMENT.md`, this tracker.
- Implementation finding: fixed-tag order payload used obsolete b-series design
  while quote/backend expected be-seen; corrected and covered by frontend unit
  regression and real browser fixed-tag order. No catalogue/pricing rule changed.
- Observed validation: both development images and production images built;
  backend suite passed 31 tests including real PostgreSQL integration and
  production Host/Origin/docs checks. Frontend npm ci, six tests and production
  build passed; production-only npm audit returned zero. Nginx config test and
  static-only runtime checks passed; actionlint passed added workflow job.
  Two production browser tests passed, two synthetic orders committed, and
  persistence/reverse proxy health survived API restart. Smoke tests use only
  new tmpfs projects and no host ports; no existing database volumes were changed.
- Test development: initial orchestration attempt inside a Python image lacked
  Docker CLI; reran with host Git Bash. First browser pass exposed an overly
  exact Font selector; corrected the selector, then both browser tests passed.
  These failed attempts are not claimed as successful verification.
- Evidence details: [production runbook](PRODUCTION_DEPLOYMENT.md),
  [Issue #4 evidence](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/4#issuecomment-6423974006),
  [Issue #5 evidence](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/5#issuecomment-6423974418).
  Final smoke assertions passed: no host port
  bindings, no persistent database mounts, URL-special password accepted by
  migrations; both browser tests and API-restart persistence passed again.
  Final production backend image rejected missing database credentials;
  changed-file credential/whitespace checks and 28 relative Markdown links passed.
- Risks/remaining gates: local HTTP smoke is not public TLS verification;
  hosting/DNS/TLS, real secret storage, protected production reviewers, hosted
  rollback/restore drill and independent review remain pending. Order submission
  is intentionally unauthenticated; edge abuse limits/retention and least-privilege
  DB account need review before real customer use. New CI job has no hosted run.
- Next owner: independent reviewer validates config and evidence; owner chooses
  hosting and separately authorizes publication/deployment. Both Issues stay open
  and existing false deployment workflow holds remain unchanged.

## Production stack publication handoff - 2026-10-26

- Task: CAP-06/CAP-09; owner: Codex implementer. User explicitly authorizes
  committing the 27 reviewed production-readiness files with
  `feat: add production stack and browser smoke tests` and a normal origin/main
  push after checks pass. No public deployment or GitHub secret/approval changes.
- Scope: publish production images/Compose, runtime security settings, fixed-tag
  regression, automated browser smoke job/tooling and supporting documentation.
  Full file inventory is in the production-preparation handoff immediately above.
- Review: all modified/untracked files belong to that scope. No real credentials
  found; production example password is empty and required at runtime. Test-only
  credentials are explicitly synthetic. No volume deletion/reset commands added;
  cleanup uses plain down against uniquely named disposable projects only.
- Safety: both deployment job conditions still begin with false publication
  holds. GitHub API returned no deployment variable names and no environments.
  CI browser smoke is implemented under contents: read, not a public deployment.
- Verification: standalone production Compose and development Compose validated
  quietly. Development Dockerfiles/compose.yml are unchanged; read-only HTTP
  checks returned 200 for UI, /@vite/client, API health/DB health and catalogue.
  Rebuilt both development/test images and production runtime/browser images;
  backend/PostgreSQL rerun passed 31 tests; frontend npm ci, six tests and build
  passed; both browser tests and restart persistence/isolation assertions passed.
  Workflow lint, quiet production Compose validation, relative links and
  credential/whitespace checks passed. Actual commit/run URLs and job conclusions
  are reported in Issues #4/#5 after push.
- Review limitations: this is implementer verification, not independent approval.
  Public DNS/TLS, provider adapter/credentials, production reviewers, actual
  dev/prod deployments, public demo, hosted rollback/restore drill and independent
  review remain pending. Vite development server is not used as production serving.
- Next owner: reviewer validates published evidence; owner separately chooses
  hosting and authorizes any deployment hold removal. Keep Issues #4/#5 open.

## Neon/Vercel preparation handoff - 2026-10-26

- Task: CAP-06 follow-up; owner: Codex implementer. User reports Neon database
  creation, but authorizes only configuration/code/documentation preparation.
  Do not read actual credentials, connect to Neon, execute any migrations,
  commit, push or deploy.
- Scope/acceptance: preserve psycopg URLs and SSL query options; separate direct
  migration and pooled serverless runtime connections; prepare guarded versioned
  migrate/seed tooling; retain local Docker behavior; document Vercel requirements.
- Files changed: `.gitignore`, `.env.neon.example`, `backend/app/db_config.py`,
  `backend/app/database.py`, `backend/alembic.ini`, `backend/alembic/env.py`,
  `backend/migrate_neon.py`, `backend/asgi.py`, `backend/.python-version`,
  `backend/.vercelignore`, `backend/tests/test_neon_config.py`, `README.md`,
  `spec.md`, `docs/ARCHITECTURE.md`, `docs/NEON_VERCEL.md`, this tracker.
- Findings/implementation: existing psycopg 3 already supports SSL options.
  Configuration accepts postgresql+psycopg and normalizes provider URL schemes,
  requires SSL for recognized Neon hosts, rejects pooled migration URLs and
  selects NullPool for Vercel/pooler connections. Existing local QueuePool and
  component credentials remain. Alembic imports pure configuration, not runtime
  engine state. The migration helper defaults to no connection; future apply
  requires explicit target confirmation and uses a direct advisory-lock session.
  Existing Alembic revisions already seed eight products/ten prices and were
  not modified. ASGI entrypoint/Python version prepared for Vercel backend root.
- Commands/results: read repository sources and official Neon/Vercel docs;
  `git status --short`; searched URL/engine usage; ran
  `docker run --rm --network none ... pytest tests --ignore=tests/integration -p no:cacheprovider`.
  All 39 offline tests passed, including nine Neon/Vercel configuration/guard
  cases, in-memory SQLite API tests and existing health/security tests. One
  existing Starlette/AnyIO deprecation warning. No migration/integration command
  or Docker stack startup was executed; no database sockets were available.
- Evidence: [Neon/Vercel runbook](NEON_VERCEL.md). Tests verify URL parsing,
  SSL and channel-binding forwarding, pool selection, direct/pooled separation,
  no-engine migration plan/target guards and offline ASGI health import.
- Risks/reviewer findings: actual Neon TLS/auth, runtime queries, connected
  migration/apply/seed verification and lock behavior remain untested by request.
  Vercel platform build/project topology, real domains/routing, secret scopes,
  preview isolation, production approval and independent review remain pending.
  Vercel Git integration can deploy independently of GitHub holds; configure its
  auto-deploy/promotion controls before linking. No live URL/credentials invented.
- Next owner: independent reviewer validates configuration and connected-path
  design; owner separately authorizes future connectivity/migration/deployment.

## Handoff template

Use this format for new or updated task records:

```text
Task ID:
Owner/role:
Scope and acceptance criteria:
Files changed:
Commands run and results:
Reviewer findings:
Risks or blockers:
Next owner:
```

## Evidence policy

Only record commands that were actually run and results that were actually
observed. Planned work must remain `Planned` or `Blocked`; it must not be marked
`Complete` merely because documentation or a proposed workflow exists.

## Vercel Hobby same-origin preparation handoff - 2026-10-26

- Task: CAP-06/CAP-09 follow-up; Codex implementer. Scope: one Vercel project
  serving built React and FastAPI /api with Neon pooled runtime credentials;
  preserve Docker configurations; no commit/push/deployment or Neon connection.
- Owner reports Neon migration head 20261025_06 and seed verification passed.
  This task did not independently connect or repeat migration/seed operations.
- Files changed this task: vercel.json, .vercelignore, frontend/vercel.json,
  frontend/src/App.tsx, backend/asgi.py, backend/app/main.py,
  backend/tests/test_health.py, backend/tests/test_production_settings.py,
  README.md, spec.md, docs/ARCHITECTURE.md, docs/NEON_VERCEL.md, this tracker.
  Existing uncommitted Neon preparation files/changes were preserved.
- Acceptance implemented: ordered service routing preserves API paths before SPA
  fallback; /api health aliases retain legacy Docker paths; production frontend
  defaults to same-origin; production Host/Origin guards remain explicit; no
  secrets/configured domains invented; pooled DATABASE_URL remains runtime-only.
- Verification observed: disposable Docker containers with --network none and
  read-only source mounts ran 42 backend tests (all passed; one existing AnyIO
  deprecation warning), six frontend tests (passed) and tsc/Vite production build
  (passed). Compiled JS contained no localhost:8000 fallback. First frontend copy
  command accidentally nested duplicate source tests; corrected copy and reran
  the exact updated sources, reporting only the final six-test result here.
  Both Vercel config files parse as JSON; 20 local Markdown links resolved;
  git diff --check passed. Docker Compose/workflow files are unchanged. No
  database containers, existing volumes, credentials or real environments touched.
- Configuration reviewed against official Vercel Services/FastAPI documentation;
  Services is beta on all plans. No Vercel CLI/platform build or hosted routing,
  CDN fallback, trusted forwarded Host, Neon TLS/query or browser test was run.
  JSON parsing is not platform schema/build validation. No fresh npm ci or
  PostgreSQL integration run is claimed by this task.
- Remaining gates: independent review, authorized publication, actual Vercel
  project/domain/origin/host/environment configuration, preview DB isolation,
  edge abuse/body controls, platform build and live synthetic-order smoke test.
  Hobby is non-commercial only; use synthetic demo orders. Git integration can
  bypass unchanged GitHub deployment holds; configure auto-deploy controls before
  linking. No full CI/CD/deployment rubric completion claimed.
- Next owner: independent reviewer and repository owner; follow exact settings
  in docs/NEON_VERCEL.md only after separately authorizing publication/deployment.

## Neon/Vercel publication handoff - 2026-10-26

- Owner/role: Codex implementer. User explicitly authorized review, validation,
  commit with feat: prepare Vercel and Neon deployment, normal origin/main push
  and inspection of GitHub Actions. No Vercel deployment, Neon changes or secrets.
- Scope: all 23 pending files from earlier Neon and same-origin preparation;
  inventories appear in the preceding two handoffs. No unrelated files found.
- Review: official current Vercel Services configuration reference supports
  service root/framework/entrypoint/build settings and ordered service rewrites.
  One repository-root project combines React/Vite and FastAPI asgi:app. Services
  remains beta; platform build, live routing/headers/Host and Neon request smoke
  tests remain unverified. Hobby remains personal/non-commercial only.
- Safety: scanned all 23 pending files without echoing secret candidates; five
  PostgreSQL URL literals are synthetic tests only. No real environment files,
  private keys or unexpected credential patterns found. Environment example
  credential values are blank; .env/.env.neon/.env.production/backend/.env and
  .vercel/project.json are ignored. No credentials staged intentionally.
  Docker/Compose files and CI/deployment workflow files have no diff against HEAD.
  Remote main matched HEAD before publication. Repository hooks/deployments were
  empty and existing check runs belonged only to GitHub Actions. No Vercel API or
  settings were accessed; GitHub deployment holds remain unchanged.
- Validation: disposable backend container with networking disabled passed all
  42 offline tests (one existing AnyIO deprecation warning). Disposable frontend
  clean npm ci reported zero vulnerabilities; six tests and production build
  passed; emitted JS has no localhost API default. JSON parsing, all pending-doc
  local links, environment ignore checks and git diff --check passed. No Neon
  connection, migration or existing-volume modification performed.
- Publication: stage only the reviewed 23 files, inspect staged names/whitespace,
  commit/push normally; actual commit and Actions job conclusions will be reported
  after publication, not predicted here. No Vercel deployment is authorized.
- Remaining requirements: independent review, real Vercel project/environment
  setup and beta build verification, preview isolation, edge abuse protection,
  hosted synthetic-order smoke checks and approved rollback demonstration.
