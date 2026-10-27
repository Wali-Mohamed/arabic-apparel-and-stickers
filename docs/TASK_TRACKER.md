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
| CAP-06 | Public deployment evidence | Hosted checks and owner production screenshot published with submission evidence; independent review pending | Repeatable deployment, public URL/demo, persistence and rollback evidence | [#4](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/4); [public demo](https://arabic-apparel-and-stickers.vercel.app/); [submission evidence](SUBMISSION.md); screenshot shows main/e9d8ef9 and live domain at capture time; hosted rollback remains unverified |
| CAP-07 | PostgreSQL integration tests and single test command | Backend unit/integration command verified; full combined runner and independent review pending, P1 | Unit/frontend and real PostgreSQL integration tests pass through one command | [#2](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/2); [test commands](SUBMISSION.md#reviewer-setup-and-tests); backend unit/PostgreSQL tests run together; frontend/browser remain separate |
| CAP-08 | Full-stack reproducibility evidence | CI browser, isolated migrations and restart persistence verified; independent review pending, P1 | Isolated Compose startup, migrations, browser flow and restart persistence are recorded | [#3](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/3); [production smoke script](../scripts/test-production.sh); successful CI 40546052593; supplements CAP-02/03 evidence |
| CAP-09 | CI/CD and rollback | CI and Vercel deployment evidenced; automatic trigger inferred; staged delivery, rollback and independent review pending, P1 | PR checks, automatic dev deploy, manual production gate and rollback evidence | [#5](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/5); [submission evidence](SUBMISSION.md#vercel-deployment-evidence-facts-versus-inference); GitHub deployment jobs remain held |
| CAP-10 | Correlated telemetry | Local pipeline, screenshots and owner log/trace navigation verified; independent review pending, P2 | Metrics, traces and structured logs share trace IDs and are viewable without customer data | [#6](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/6) |
| CAP-11 | User-impact alert | Published local firing/notification/recovery verified; screenshots and independent review pending, P2 | Reversible isolated fault demonstrates firing and recovery | [#7](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/7); depends on CAP-10 |
| CAP-12 | Bounded on-call agent | Local real-model investigation/remediation/recovery verified; screenshots and independent review pending, P2 | Alert triggers agent diagnosis/remediation and demonstrated recovery | [#8](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/8); depends on CAP-11; [runbook](ONCALL.md) |
| CAP-13 | Grading evidence and independent review | Submission guide and rubric map prepared; independent review and peer reviews outstanding, P1 | All current criteria mapped to verified evidence; remaining gaps and submission obligations recorded | [#9](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/9); [submission guide](SUBMISSION.md); estimated 22/24 conservative, 23/24 conditional on automatic CD acceptance |

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

## Fixed Be Seen bidirectional display handoff - 2026-10-26

- Owner/role: Codex implementer; user requests a local-only display correction.
  Acceptance: both Small/Big tags show English Be on the left and Arabic seen
  on the right in isolated script spans, consistently across cards, live preview,
  fixed-design details, order summary and successful order confirmation. Preserve
  non-editable design, API payloads, prices, existing orders and unrelated products.
- Findings: Small preview inherited RTL around mixed text; Big preview incorrectly
  used the generic Arabic personalization placeholder. Only Small previously had
  a fixed-design detail. No database metadata change is needed for rendering.
- Implementation: one BeSeenDesign component uses dir=ltr, inline-flex row layout
  and unicode-bidi:isolate, with separate English LTR and Arabic RTL/lang spans.
  Both tag slugs use this renderer throughout the applicable frontend views.
  Personalized products keep their RTL previews and existing validation controls.
  Small payload remains design=be-seen; Big remains empty options as required by
  the current backend. No Alembic/backend/API/pricing/order data changes.
- Files changed: frontend/src/App.tsx, frontend/src/App.test.tsx, README.md,
  spec.md, docs/ARCHITECTURE.md and this tracker.
- Verification observed: disposable containers with --network none and read-only
  repository mounts ran 42 backend tests (passed; one existing AnyIO deprecation
  warning), eight frontend tests (passed) and TypeScript/Vite production build
  (passed). Two parameterized product-flow regressions exercise RTL ancestors,
  child text/order/isolation, both card/preview/summary/confirmation designs,
  absence of editable Arabic/font controls and unchanged quote/order payloads.
  git diff --check passed. No remote service or existing database/volume touched.
- Limits/next owner: frontend tests verify DOM and layout declarations, not pixel
  positions in a real browser. Independent browser/visual review remains pending.
  No commit, push or deployment performed; owner reviews before publication.

## Be Seen display fix publication handoff - 2026-10-26

- Owner/role: Codex implementer. User authorizes review of the six-file fix,
  frontend validation, commit fix: correct Be Seen tag text direction and normal
  origin/main push, followed by CI and Vercel production status inspection.
- Reviewed files: frontend/src/App.tsx, frontend/src/App.test.tsx, README.md,
  spec.md, docs/ARCHITECTURE.md and this tracker. No unrelated diff or credential
  patterns found. No backend, prices, orders, migrations or Neon credentials changed.
- Validation: disposable offline frontend container passed all eight tests and
  TypeScript/Vite production build. Both tag regression flows verify English
  first/Arabic second in isolated LTR flex layout under an RTL ancestor, across
  card/preview/summary/confirmation, and preserve fixed-design request payloads.
  git diff --check passed; origin/main matched HEAD before publication.
- Review remains implementer verification; independent browser pixel-position
  verification has not been performed. Existing preceding handoff records backend
  regression evidence. This publication does not connect to Neon or submit orders.
- Status before publication: GitHub returned no deployments and no Vercel check
  runs for current main; Vercel CLI unavailable locally. Inspect the newly pushed
  commit's Actions/check/status/deployment metadata and report actual results.
  No direct Vercel deployment is initiated or real secrets configured by this task.

## Public deployment evidence review - 2026-10-26

- Scope/owner: Codex implementer reviewed Issue #4 acceptance criteria under owner
  authorization to post verified public evidence and update this tracker only.
  No application edits, commit, push, migration or deployment authorized/performed.
- Public app: https://arabic-apparel-and-stickers.vercel.app/ (React/FastAPI on
  Vercel; Neon provider and successful demo order/Small+Big visual order are
  owner-confirmed). These owner reports are distinct from the agent checks below.
- Observed checks: public GET /, /api/health, /api/health/db and /api/products all
  returned HTTP 200; DB health reported connected; catalogue contained eight
  products. Non-persisting Small-tag quote POST returned HTTP 200, quantity 1,
  total 500 integer GBP pence and exact matching public-origin CORS response.
  No order was created and no customer/order records or credentials accessed.
- Release: commit 690f99ec35e964c80c2e78315678c1a964a52369; latest successful main
  [CI run 40412574765](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/actions/runs/40412574765)
  passed backend, frontend, PostgreSQL integration, both Docker builds and
  production browser smoke. Vercel GitHub status SUCCESS/Deployment has completed:
  [deployment dashboard](https://vercel.com/aim-aster/arabic-apparel-and-stickers/8tiaxVBxJ18aEHyruo2FXBjennrC).
  Dashboard access and direct production-alias-to-SHA mapping were not available.
  GitHub development deployment was skipped; Issue #5 CD gates remain separate.
- Evidence posted: [Issue #4 review comment](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/4#issuecomment-6428990374).
  Issue #4 remains OPEN: README has no public URL and still says no deployment;
  independent hosted browser/order persistence and historical approval evidence
  remain unrecorded, and the required independent reviewer has not approved.
  Rollback procedure exists in NEON_VERCEL.md; hosted rollback/restore drill is
  not claimed. Historical no-deployment handoffs describe their original dates.
- Files changed: docs/TASK_TRACKER.md only. Commands: gh issue view/run list/run
  view/commit-status; public HTTPS GETs and read-only pricing POST via PowerShell;
  gh issue comment; git diff --check and local link validation. Web-reader access
  failed; direct HTTPS requests supplied the actual observed public results.
- Next owner: authorized documentation update/publication of README URL and stale
  deployment claims; independent reviewer confirms hosted quoting/order persistence,
  visual behavior and approval evidence. Keep synthetic data private; do not
  expose real order/contact records. No full deployment/CI-CD completion claimed.

## Public deployment documentation finalization - 2026-10-26

- Owner/role: Codex implementer; authorized README/tracker updates, Issue #4
  evidence and non-destructive hosted review, including one permitted unique
  synthetic order. No commit, push, code/schema/price/migration or secret changes.
- README now links https://arabic-apparel-and-stickers.vercel.app/ and documents
  compiled React/Vite and FastAPI in one Vercel Services project, same-origin /api,
  pooled SSL Neon connection, separate direct operator migrations, local Docker
  distinction, no-payments/non-commercial scope and reviewer browser steps.
  Removed current no-deployment assertions; historical handoffs remain history.
- Hosted results: GET /, /api/health, /api/health/db returned 200; catalogue had
  eight products. Valid Arabic rectangular-tag quote (Amiri, quantity 1) returned
  1200 pence. Exactly one unique synthetic order with example.invalid contact
  returned HTTP 201, ID 5, status new, quantity 1, total 1200 pence, created_at
  2026-10-26T22:44:48.815057Z. Returned total matched quote; subsequent DB health
  remained connected. No real customer details or unique contact marker published.
- Persistence evidence boundary: source handler commits and refreshes before
  returning 201, supporting a committed database write. No public order-read
  route exists; no independent later SQL retrieval, restart/restore or direct
  deployed-source-to-SHA inspection occurred. No automatic retry or deletion.
- Latest reviewed release 690f99ec35e964c80c2e78315678c1a964a52369 and successful
  [six-job CI](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/actions/runs/40412574765)
  were reconfirmed. Owner visual confirmations are not independent human review.
- Public handoff: [Issue #4 finalization evidence](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/4#issuecomment-6429118340).
- Rubric assessment: official Deployment 2-point criterion requires deployed and
  publicly reachable application or a clear deployment demo. Observed live
  frontend/API/catalogue/quote/order support that criterion; this is not an awarded
  grade. Issue #4 remains open for authorized documentation publication, independent
  review and recorded historical deployment approval. Later narrow synthetic-row
  retrieval and hosted rollback drill would strengthen evidence; full Issue #5
  CI/CD acceptance remains separate. No human peer review is claimed.
- Files changed: README.md and docs/TASK_TRACKER.md only (tracker contained prior
  uncommitted evidence, preserved). Commands: gh issue view/run list/comment;
  sanitized hosted GET/quote/one order POST; local links and git diff --check.
- Next owner: review and authorize documentation commit/push; independent reviewer
  follows README walkthrough and, if authorized, confirms only the synthetic row
  without exposing customer data. No application tests rerun for documentation.

## Deployment evidence publication handoff - 2026-10-26

- User authorizes review, commit and normal origin/main push of README.md and
  this tracker only, followed by CI inspection and an Issue #4 commit-link update.
- Reviewed scope: live URL, Vercel/FastAPI/Neon architecture, reviewer steps,
  sanitized historical hosted checks and synthetic order 5 evidence. No secrets
  or unrelated changes found. Restored two historical lines accidentally affected
  by PowerShell text encoding during prior tracker updates.
- Local Markdown links and git diff --check validated before publication. No
  application/schema/pricing/order changes or new hosted writes performed.
- Issue #4 remains open for independent review and recorded historical deployment
  approval evidence; later SQL retrieval/rollback drill are not claimed. Actual
  commit and Actions results will be reported in Issue #4 after publication.

## Phase 1 local observability handoff - 2026-10-26

- Owner/role: Codex implementer under explicit local-only authorization for
  Issue #6. No commit/push/deployment, Vercel/Grafana Cloud secrets or Neon access.
- Scope/acceptance: catalogue, personalized pricing and demo-order request spans,
  request/status/error/duration metrics, JSON logs with trace/span IDs, optional
  pinned local LGTM storage/UI, privacy and outage isolation, repeatable tests.
- Implementation: OpenTelemetry SDK/HTTP exporter 1.45.1; manual SERVER request
  spans and fixed child operation names. Strict field allowlist, no auto HTTP/SQL
  instrumentation, exception messages/events, bodies, names/contacts, Arabic text,
  raw URLs/query strings, headers/cookies/tokens, SQL statements/parameters or
  order IDs. Trace IDs use exemplars, not metric labels. Optional init plus bounded
  background export/timeouts preserve APIs when the collector is unavailable.
- Local stack: standalone compose.observability.yml, grafana/otel-lgtm:0.38.1,
  loopback UI 3000/frontend 18080, private OTLP/storage ports, isolated tmpfs
  PostgreSQL seeded only with existing revisions. Existing Compose/CI/Vercel
  config and migrations unchanged. No existing volumes or orders touched.
- Files: backend/app/{telemetry,main,products,orders}.py,
  backend/requirements.txt, backend/tests/test_telemetry.py,
  compose.observability.yml, observability/{dashboard.json,dashboards.yaml,datasources.yaml},
  scripts/{observability-demo.py,observability-ui.cjs}, README.md, spec.md,
  docs/ARCHITECTURE.md, docs/OBSERVABILITY.md and this tracker.
- Observed tests: 46 passed in isolated migrated PostgreSQL + backend suite;
  final offline suite 45 passed after SERVER-span refinement; eight frontend
  tests and production build passed. Backend/static/browser images built.
  Tests cover same trace/span IDs, distinct request traces, 200/201/422/500
  metrics, sensitive sentinels, SDK exemplars and committed order under exporter
  failure. Existing AnyIO deprecation warning only. Initial 500 fixture used a
  Starlette route without FastAPI route metadata; corrected and reran successfully.
- Actual storage: demo script verified catalogue/Arabic quote/synthetic order/422,
  fresh per-run stored metrics/logs/trace correlation via Grafana datasource
  proxies. Final run found four fresh stored exemplars; one resolved to a retained
  trace. Fresh order trace cc892754c194718c4fc7aefb4c4a9a4c. Earlier replay used
  older log entries; narrowed query to the current run and reran to avoid stale
  evidence. Chromium rendered all four provisioned dashboard panels.
- Outage: stopped LGTM, submitted one synthetic order in disposable DB, got 201,
  and a separate database session confirmed persistence; collector restarted.
  Harness quoting/hard-coded obsolete ID attempts failed before any order write;
  corrected with stdin Python and actual catalogue slug resolution.
- Commands: docker build; offline docker run pytest/npm test/npm run build;
  isolated compose.ci.yml run --build --rm backend; observability up/demo/browser;
  collector stop/start + local order/DB check; Compose/JSON/link/whitespace checks.
  Disposable CI and observability review projects cleaned using plain down,
  never down -v. No hosted API request or customer record read in this task.
- Public handoff: [Issue #6 implementation evidence](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/6#issuecomment-6429573243).
- Remaining: no screenshot artifact, manual exemplar click-through or Explore
  trace UI navigation; no independent reviewer, published code or new Actions run.
  Stored exemplars and automatic dashboard-panel rendering ARE observed, not just
  configured. Real-LGTM demo/UI check is not wired into CI; existing backend CI
  discovers unit telemetry tests only after later authorized publication.
  Vercel lifecycle/flush and hosted monitoring are Phase 2, not claimed here.
- Next owner: independently reproduce docs/OBSERVABILITY.md, capture sanitized
  screenshot/navigation evidence, review privacy/outage behavior, then owner
  separately authorizes publication. Keep Issue #6 open; no awarded grade claimed.

## Observability publication handoff - 2026-10-26

- User explicitly authorizes review, validation, commit with feat: add correlated
  OpenTelemetry observability and normal origin/main push, then Actions inspection
  and Issue #6 evidence update. Monitoring remains LOCAL ONLY; no Cloud/Vercel
  monitoring variables, database migrations, existing orders or Neon changes.
- Reviewed all Phase 1 instrumentation, privacy fields, failure handling,
  provisioning, Compose, scripts/tests and documentation. Existing API prices,
  validation and transaction semantics preserved. Nineteen task files include
  the two owner-supplied screenshots in the existing observability directory.
- Screenshots visually inspected: observability/observability-dashboard.png
  shows four populated panels; observability/observability-log-trace-correlation.png
  shows matching trace 5316df8ecc0cd03160fcf54cab35451e and a four-span 422 pricing
  trace. No credentials/customer/contact/personalization data visible. Relative
  image links added to OBSERVABILITY.md; owner manual verification is not an
  independent reviewer sign-off. Manual metric-exemplar navigation not claimed.
- Publication validation: 46 backend tests passed including real migrated tmpfs
  PostgreSQL integration and telemetry correlation/privacy/failure/SDK exemplar
  cases. Clean npm ci reported zero vulnerabilities; eight frontend tests and
  TypeScript/Vite build passed. Actual fresh storage demonstration returned four
  exemplars, one resolved to Tempo; matching order trace
  d56a403a9c33bed3624cfb470db034b0. Existing AnyIO warning remains.
- Initial verification stack start failed because the owner's port 3000 was
  occupied; left existing services untouched. Added configurable loopback ports
  LOCAL_GRAFANA_PORT/LOCAL_FRONTEND_PORT (defaults unchanged), tested on 3001/18081.
  Initial browser rerun failed during startup; added explicit Grafana HTTP health
  readiness polling without removing panel assertions, then reran. Record final
  browser result in the publication response/Issue #6 rather than hiding failure.
- Existing plain Compose, production Compose, migrations, GitHub workflows,
  frontend application code and Vercel config have no diff. Secret-pattern and
  screenshot review found no real secrets; ephemeral demo DB credentials are
  explicitly local-only. Local links, JSON and git diff --check passed.
- This commit publishes the implementation/evidence; actual commit SHA and
  Actions conclusions will be added to Issue #6 after push. Required independent
  review remains outstanding; keep Issue #6 open. Local correlated monitoring
  supports the rubric's 2-point criterion, not an awarded grade or production
  monitoring claim. Real-LGTM/UI scripts are not yet automated in hosted CI.

## Phase 2 local pricing alerting handoff - 2026-10-27

- Owner/role: Codex implementer under explicit local-only authorization for
  Issue #7. No commit, push, deployment, Vercel/Neon changes or existing-order
  writes. Required independent review is still outstanding.
- Scope: provisioned Grafana PricingUnavailable on existing pricing POST request
  counter, >=5 5xx in 2m, 10s evaluation, 30s pending, exclude 4xx. KeepLast on
  NoData/Error plus explicit Error/NoData reason checks; no false recovery on
  datasource failure. Internal webhook stores only safe alert/state/timestamp/
  fingerprint fields, bounded in memory; no external notifications.
- Fault: explicit local flags + exact disposable DB identity, Vercel/CI/integration
  blocks, private container marker, valid pricing returns sanitized 503 without
  any write. Invalid inputs still 422. No fault-control HTTP endpoint. Context/
  finally and PowerShell cleanup remove marker after errors; no order retries.
- Files: backend/app/local_faults.py, backend/app/alert_webhook.py,
  backend/app/products.py, backend/tests/test_alerting.py, compose.alerting.yml,
  observability/alerting.yaml, observability/datasources.yaml (local editable
  metrics datasource for reversible query-outage test), scripts/alerting-demo.py,
  scripts/alerting-ui.cjs, scripts/test-alerting.ps1, docs/ALERTING.md, README.md,
  spec.md, docs/ARCHITECTURE.md and this tracker. Existing Compose/CI/Vercel
  configurations, migrations, prices, catalogue and order handler are unchanged.
- Actual final fresh-project run (UTC/London): Normal 10:36:54.726077; Pending
  10:38:40.497394; Alerting observed 10:39:11.745210. Firing receipt
  10:39:10.028921, incident start 10:39:10; monitoring unknown while still firing
  10:39:42.880977; datasource healthy/pricing recovered around 10:40:11.723189;
  resolved receipt 10:41:40.652989; Normal observed 10:41:42.439649. Matching
  fingerprint 104cd504dd74996e. Failed pricing log resolves to Tempo trace
  3577ac6348cbcfcb397701037a5bc938. No fake states or synthetic metric insertion.
- Demonstrated: sustained 422s and three 503s stayed Normal; sustained actual 503s
  caused Pending/Firing; real datasource query failure retained firing, with no
  false resolved receipt; removal restored pricing 200 and automatic resolution.
  Grafana can report root rule health=ok under Error, KeepLast, so verifier also
  checks Alertmanager's grafana_state_reason. Fresh receipts/clean metric baseline
  prevent stale events satisfying tests. Chromium verified actual rule detail UI.
- Validation: 57 backend tests passed with real isolated migrated PostgreSQL
  integration; final offline suite 56 passed; eight frontend tests and production
  build passed. Covers guards, API behavior, cleanup failures, sanitized webhook,
  telemetry privacy/exporter-failure regressions. One existing AnyIO warning.
  Full PowerShell wrapper starts stack, verifies all stages, runs UI check and
  confirms marker cleanup/plain down. All verification stacks used unique project
  names and tmpfs DB; cleaned with plain down, no volume deletion/reset.
- Earlier failures: misplaced unit-test block, over-escaped Grafana expression,
  read-only metrics datasource rejecting the outage test, KeepLast health reason
  initially misinterpreted, and collapsed list UI controls. Fixed and reran from
  a fresh project; final wrapper passed including UI and cleanup. Not hidden or
  counted as successful tests. Initial debug projects were also cleaned safely.
- Evidence: [Issue #7 implementation review](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/7#issuecomment-6439954499).
  Reproduce with ./scripts/test-alerting.ps1; use -KeepStack for screenshots;
  default Grafana 3010/app 18100, configurable ports. See docs/ALERTING.md.
- Publication safety: draft issue comment was rejected by automatic approval
  review for including a local default login; removed that detail and posted
  sanitized evidence successfully. No rejected content was posted or bypassed.
- Remaining: manual screenshots/state-history review and independent reviewer
  approval, then separately authorized code publication. Runbook annotation's
  future GitHub URL is pending publication. No new Actions run or production
  monitoring claimed. The local demonstration supports the 1-point alerting
  criterion, not an awarded grade. Total outages/frozen telemetry need separate
  availability coverage; receiver is ephemeral/local only; no AI agent yet.

## Alerting publication validation - 2026-10-27

- Owner authorized review, commit and normal push for Issue #7. This is the
  implementing agent's review, not independent approval. No live configuration,
  schema, prices, existing orders or Neon credentials changed.
- Revalidated 57 backend tests including isolated PostgreSQL integration after
  all six existing Alembic revisions; eight frontend tests and production build
  passed. npm ci reported zero vulnerabilities. Existing AnyIO warning remains.
- Both CI and observability+alerting Compose configurations validate; 26 local
  documentation links resolve; PowerShell syntax and git diff --check pass.
  An initial link-check command had shell quoting errors; the corrected
  PowerShell link check passed without changing implementation.
- Reviewed all 15 pending files: fault requires explicit local flags, exact
  disposable DB identity and absence of VERCEL/CI guards. Webhook allowlist
  excludes customer payloads and credentials; receiver has no published port.
  Only synthetic local/demo connection details are present. Deployment holds
  and existing application/production settings remain unchanged.
- Retained lifecycle evidence above remains the source for firing/resolved/UI
  verification; the multi-minute demonstration was not rerun. No failed
  verification requires a new demonstration.
- Commit, push and hosted CI evidence will be linked in Issue #7 after publication.
  Keep the issue open for manual screenshots and independent reviewer validation.

## Issue #8 local AI on-call implementation - 2026-10-27

- Scope/owner: Codex implementer under explicit local implementation and real-model
  demonstration authorization. No commit, push, hosted deployment, production
  Vercel/Neon access, existing-order writes or schema/catalogue/price changes.
- Acceptance: authenticated real firing webhook automatically starts a bounded
  Python worker; diagnose actual Prometheus/Loki/Tempo and current synthetic
  pricing; local model chooses allowlisted action; deterministic gates allow
  one predefined marker removal; verify HTTP 200, healthy Normal and matching
  resolved receipt. Independent reviewer validation is still required.
- Implementation: dedicated standalone compose.oncall.yml; internal runtime
  network, separate bootstrap download service, no published model/worker ports,
  no Docker socket or host-source mount, no database/cloud credentials in worker.
  Disposable fault tmpfs and SQLite ledger are separate from existing DB volumes.
  Original scripts/test-alerting.ps1 and regular Compose/Vercel config unchanged;
  .vercelignore gains only an exclusion for generated secret artifacts.
- Webhook: ephemeral local Bearer secret in ignored files; constant-time auth,
  strict schema/size/timestamp/alert/environment checks, fingerprint+start dedup,
  single worker, restart escalation, no raw annotations/body/exception logging.
  Eight tools maximum, one remediation, five-second HTTP requests, 90-second
  model inference bound, ten-minute incident deadline; no external escalation.
- Fault: backend attestation requires existing disposable DB guard, shared fixed
  marker directory; worker rejects VERCEL/CI/integration/database credentials.
  Gate checks fresh failures, matching 503 log/request trace, current 503 quote,
  marker and healthy firing Grafana incident matching fingerprint and start.
  Production/default marker behavior preserved. Model cannot choose paths/URLs,
  queries or shell commands. Tiny model sees compact typed evidence only.
- Versions: Ollama 0.6.8, image sha256:50ab2378567a62b811a2967759dd91f254864c3495cbe50576bd8a85bc6edd56;
  qwen2.5:0.5b (494M Q4_K_M), digest
  a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67.
  Tested with Docker allocation ~8 GB RAM / 4 CPUs, no GPU or paid API.
- Actual first attempt: apparel-oncall-3debcca40d FAILED; automatic firing received
  16:41:14 UTC, all real diagnostics retrieved, actual model chose escalation at
  16:41:26 despite sufficient evidence. No agent removal; failure recorded before
  fallback cleanup. observability/oncall-failed-attempt.json preserves evidence.
  Simplified model facts/prompt and retried with the same model and permission gates.
- Actual successful retry: apparel-oncall-5a385a1757, wrapper exit 0 / PASSED.
  UTC: firing/activation 16:45:10.045527; model decision 16:45:22.173844 (16 output
  tokens); agent removed marker 16:45:22.316141; HTTP 200 probes 16:45:22.425093
  and 16:45:24.516684; resolved received 16:47:30.460899; Recovered with healthy
  Normal 16:47:31.544243. Incident fingerprint 104cd504dd74996e, start 16:45:10;
  failed trace 37b0e3c89638e031627253e097e736ea. Seven tools / one remediation;
  driver observed 27 actual 503s. No fabricated metrics, states or notifications.
- Transcript: observability/oncall-transcript.json; ignored original runtime
  .oncall-local/apparel-oncall-5a385a1757/transcript.json. Never publish its sibling
  secret or generated alerting.yaml. Sanitized copies contain no credentials,
  bodies or customer fields. Fallback cleanup starts only after outcome recorded;
  it is not part of the agent-success assertion. Both demo stacks were stopped.
- Validation commands/results: isolated compose.ci.yml backend run passed 93 tests
  including PostgreSQL integration after existing Alembic migrations; final
  pytest tests/test_oncall.py -q passed 36 tests. Frontend npm ci, eight tests and
  production build passed (zero npm vulnerabilities reported). Compose config
  --quiet, PowerShell AST parse, local Markdown links and git diff --check passed.
  Existing AnyIO warning remains. No failing automated test was bypassed; first
  real-model failure explicitly retained above. Existing DB volumes not deleted.
- Files: .gitignore, .vercelignore, README.md, spec.md, backend/app/local_faults.py,
  backend/app/oncall.py, backend/app/oncall_arm.py, backend/tests/test_oncall.py,
  compose.oncall.yml, scripts/oncall-demo.py, scripts/test-oncall.ps1,
  docs/ONCALL.md, docs/ARCHITECTURE.md, docs/AI_AGENT_WORKFLOW.md, this tracker,
  observability/oncall-transcript.json and observability/oncall-failed-attempt.json.
- Remaining: independent reviewer and manual Grafana lifecycle screenshots;
  separate authorization for publication. Keep Issue #8 open. Local demonstration
  supports two-point on-call behavior, not an awarded grade or production agent.
  Small-model reliability is limited (first failure observed); unknown incidents,
  stale/unavailable telemetry, bad decisions and timeouts escalate locally.
- Public evidence handoff: [Issue #8 implementation and real-model results](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/8#issuecomment-6448000090).
  Issue remains OPEN. Final check resolved 33 local documentation links; secret
  pattern scan found no real token/private-key/Neon URL in the 17 changed files.
  Nothing staged, committed or pushed.

## Issue #8 publication review - 2026-10-27

- Owner explicitly authorized review, commit and normal push. Reviewed all 17
  pending files; implementing-agent review is not independent human approval.
  Corrected tracker formatting and updated current publication wording only.
- Both retained transcripts parse and pass field/privacy review: no credentials,
  personal data, raw model reasoning or unsafe filesystem paths. The failed
  attempt has escalation and no removal; successful attempt has exactly one
  removal, repeated 200 probes, matching resolved receipt and healthy recovery.
  Driver normal flow never removes the marker; fallback cleanup follows the
  recorded outcome. No full real-model demonstration was rerun.
- Security review confirms ephemeral authenticated webhook, deduplication,
  bounded tools/model output, fresh-evidence/active-incident gates, Vercel/CI
  exclusions, no cloud or database credentials or Docker socket in the worker,
  and internal-only runtime networking. Generated secrets remain Git/Vercel
  excluded. Existing application data, migrations and production settings unchanged.
- Fresh validation: 93 backend tests including disposable PostgreSQL integration
  after six existing Alembic revisions passed; eight frontend tests, npm ci and
  production build passed (zero reported npm vulnerabilities). Compose quiet
  validation and PowerShell syntax passed; existing AnyIO warning remains.
- Commit and Actions results will be linked in Issue #8 after publication.
  Keep issue open for independent review and manual Grafana screenshots.

## Final submission documentation and Vercel evidence - 2026-10-27

- Owner authorized documentation/screenshot review, commit and normal push.
  Scope: README.md, spec.md, docs/ARCHITECTURE.md, docs/ALERTING.md,
  docs/TASK_TRACKER.md, new docs/SUBMISSION.md and owner-provided
  docs/evidence/vercel-production-deployment.png. No application, database,
  prices, orders, cloud credentials or Vercel configuration changes.
- Screenshot exists (112631 bytes) and visual inspection confirms Ready/Latest,
  Production/Current, source main, e9d8ef9 and the production domain at capture
  time. No visible secrets/customer data. This is supplied owner evidence,
  not an independent provider audit or proof of the deployment trigger.
- GitHub CI 40546052593 rechecked: all six jobs succeeded for full SHA
  e9d8ef914c056bf2da6754f78bdea26dda8edcad. Vercel bot Pending at 16:58:03 UTC,
  Success at 16:58:32, same deployment record AaevsyrhBfRpfh66i2rtPVomfkPj.
  CI ended 16:59:23, so no Vercel dependency on completed CI is claimed.
  Automatic Git triggering remains strongly supported inference; provider API
  metadata was unavailable (403), and absence of manual intervention unverified.
- Corrected current preparation-only deployment/on-call statements and tracker
  summaries. Historical execution records remain historical. Guide includes all
  12 exact criterion maxima, evidence, isolated tests/demos, local-only monitoring,
  privacy boundaries, failed/successful AI transcripts and owner Grafana images.
- Score remains 22/24 conservative or 23/24 if automatic Vercel CD evidence is
  accepted; no 24/24 claim. Independent review, manual alert/on-call lifecycle
  screenshots, three required peer reviews, staged dev/manual prod delivery and
  hosted rollback remain outstanding. No issues closed or manual deployment run.
- Validation: documentation links, credential/scope review and git diff --check
  performed before staging. Application tests and full demos were not rerun for
  this documentation-only change; publication Actions results are reported in
  the final handoff, distinct from the e9d8ef9 baseline above.
- Final local validation: 67 relative links and four heading anchors resolve;
  PNG has no text/EXIF metadata chunks; credential-pattern and whitespace checks
  pass. Exactly seven documentation/evidence files are selected for publication.
