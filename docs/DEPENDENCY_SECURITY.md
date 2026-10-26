# Frontend dependency security review - 2026-10-26

## Baseline and dependency chains

`npm audit --json` was run in `/app`, the frontend directory in the running
frontend container, before changing manifests. It reported six affected package
entries (not six independent advisories): three moderate, one high, two critical.
The [raw baseline](security/npm-audit-before.json) retains every advisory,
affected version range and npm fix recommendation.

| Package | Severity | Installed affected chain | Available remediation |
| --- | --- | --- | --- |
| vitest 2.1.9 | Critical | Direct devDependency | No patched 2.x; UI-server advisory fixed in 3.2.6, but later mocker advisories require at least 4.1.12 for this complete remediation |
| @vitest/mocker 2.1.9 | Moderate | vitest -> @vitest/mocker | Redirect traversal fixed in 4.1.11, manual mock injection fixed in 4.1.12; use matching Vitest release |
| tinypool 1.1.1 | Critical | vitest -> tinypool | Advisories require 2.1.2+; selected Vitest 4 no longer depends on it, avoiding an unsupported transitive major override |
| vite 5.4.21 | High | vitest -> vite; vitest -> vite-node -> vite; mocker uses that nested Vite | Remove vulnerable nested Vite through Vitest upgrade; existing direct Vite 6.4.5 is outside the audited affected ranges |
| esbuild 0.21.5 | Moderate | vitest -> vite -> esbuild; vitest -> vite-node -> vite -> esbuild | Fixed in 0.25.0+; removing nested Vite leaves direct Vite's existing esbuild 0.25.12 |
| vite-node 2.1.9 | Moderate | vitest -> vite-node -> vulnerable vite | Metavulnerability from Vite; Vitest 4 replaces vite-node with Vite's module runner |

npm suggested Vitest 5.0.5 as a major update. Registry metadata and audit ranges
showed 4.1.12 also covers these findings while supporting current Vite 6/Node 22.
The direct production dependencies are React and React DOM; the before-change
`npm audit --omit=dev --json` reported zero vulnerabilities.

## Exposure assessment

- These six entries belong to devDependencies, not the browser production
  dependency graph. Test runner, worker pool and dev servers are not shipped as
  runtime modules in a built React static bundle.
- The UI-server RCE advisory requires a listening Vitest UI server. `npm test`
  uses `vitest run`; no @vitest/ui package, browser test server or UI invocation
  is configured here. Mocker issues involve exposed browser/mock endpoints;
  current tests use jsdom and fetch stubs rather than browser mode.
- Tinypool findings concern prototype-pollution gadgets reaching worker options;
  this does not establish a remotely exploitable application endpoint. Untrusted
  tests still execute code by design: run PR tests without deployment secrets.
- Vite/esbuild findings concern dev-server file access, cross-origin behavior
  and editor integrations (some Windows-only). The vulnerable copies were nested
  under Vitest; direct Vite 6.4.5 was not flagged by this audit.
- The current Dockerfile installs development tools and runs `vite --host
  0.0.0.0`, so devDependency classification alone does not make a deployment safe.
  Do not expose this development container publicly. Use a production static
  server for the built assets before public hosting. There is no verified public
  deployment whose running image can be declared fixed by these local changes.

## Remediation and compatibility

Pinned Vitest to 4.1.12 and regenerated package.json/package-lock.json together
from the existing lock. React, Vite, TypeScript, jsdom and plugin major versions
are unchanged. The upgrade was explained before applying it; no forced audit
fix or ad hoc transitive overrides were used.

Vitest 4 changes mocking/worker internals and requires Node >=20 and Vite >=6;
Docker and CI use Node 22. Tests use supported jsdom, globals, setupFiles,
vi.fn and vi.unstubAllGlobals APIs. No application or test-assertion changes were
needed. Transitive test libraries change with Vitest, including Chai 5 to 6;
this is covered by running the existing test suite.

Two npm 10 attempts failed with `Cannot read properties of null (reading
'edgesOut')` without modifying manifests. npm 11 was used only inside a disposable
container for the update. The normal Docker image's npm 10 `npm ci` subsequently
accepted the new lock and reported zero vulnerabilities. No existing Docker
volume or PostgreSQL data was changed.

Sources: [Vitest migration](https://v4.vitest.dev/guide/migration.html),
[UI server advisory](https://github.com/vitest-dev/vitest/security/advisories/GHSA-5xrq-8626-4rwp),
[mocker traversal](https://github.com/advisories/GHSA-82fw-gwwq-j7x9),
[mocker injection](https://github.com/advisories/GHSA-qxg6-89mg-rqv8),
[worker gadget](https://github.com/tinylibs/tinypool/security/advisories/GHSA-85c8-ppgw-ccpr),
[esbuild advisory](https://github.com/advisories/GHSA-67mh-4wv8-2f99).

## CI/CD credential and permission review

Reviewed all three workflow YAML files, scripts/deploy.sh, scripts/test-deploy.sh
and both .dockerignore files. CI grants only contents: read. Deployment adds
actions: read for successful-CI lookup; it does not request write-all, package
publication, id-token or repository write permissions. Unspecified permissions
are not granted. Checkout uses persist-credentials: false.

CI has no hosting secrets. The visible database password is for the disposable
test database only. Deployment tokens and webhook URL are environment secret
references, injected only into the deployment step; the client has no xtrace,
verbose curl or provider response output. Test credentials are explicitly fake
and tools are mocked. Docker contexts exclude .env files. Credential-pattern
checks and workflow lint complement this manual inspection, not a proof that
every possible secret is detectable.

Deployment is restricted to trusted main-push CI or manual main dispatch,
checks successful CI for the exact SHA, and is held by explicit `false &&` job
conditions as well as enable variables. A reviewed code change is needed to
remove the holds after hosting setup. Production required reviewers must still be configured in GitHub;
declaring environment: production alone is not approval. Actions currently use
version tags rather than immutable commit pins, an optional supply-chain
hardening follow-up; no excessive token permissions were found.

## Before/after and observed verification

| Audit scope | Before | After |
| --- | --- | --- |
| Full dependency tree | 6: 3 moderate, 1 high, 2 critical | 0 |
| Production dependencies (`--omit=dev`) | 0 | 0 |

Raw results: [before](security/npm-audit-before.json),
[after](security/npm-audit-after.json),
[production after](security/npm-audit-production-after.json).

The standard frontend Dockerfile built successfully as
`apparel-frontend-audit:verified`. A fresh container without mounted volumes ran
`npm ci && npm test && npm run build`, then `npm ls` and both audit modes:
all five tests passed with Vitest 4.1.12, TypeScript/Vite production build passed,
and both audits returned zero. `npm ls` confirmed Vite 6.4.5 and esbuild 0.25.12,
with no nested vulnerable Vite, vite-node or tinypool. Workflow actionlint passed.
No Postgres service, migration, data or existing Docker volume was modified.

The already-running frontend container still has its old node_modules volume;
it was used only for the baseline audit, not modified or restarted. These fixes
are in the manifests and newly verified image. Updating that old local runtime
requires a later deliberate dependency refresh; its old install is not evidence
that the new lockfile is vulnerable. Do not publish an old image.

Recommendation: the npm findings are resolved for the newly built frontend,
and this dependency change is suitable for source publication after independent
review. This is not a complete application security audit or public-hosting
approval. Public hosting still needs production static serving, backend production
configuration, HTTPS/API/CORS setup and the deployment protections in
[CI/CD setup](CI_CD.md). Keep dev/test servers private. No public deployment was
performed, and no existing hosted runtime was verified. Audit results are a dated
registry snapshot; rerun before release.
