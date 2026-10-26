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
| CAP-06 | Public deployment evidence | Blocked on deployment approval | Repeatable deployment, public URL/demo, persistence and rollback evidence | [#4](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/4); no deployment performed |
| CAP-07 | PostgreSQL integration tests and single test command | Planned, P1 | Unit/frontend and real PostgreSQL integration tests pass through one command | [#2](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/2); current API tests use SQLite, UI tests mock fetch |
| CAP-08 | Full-stack reproducibility evidence | Planned, P1 | Isolated Compose startup, migrations, browser flow and restart persistence are recorded | [#3](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/3); supplements CAP-02/03 evidence |
| CAP-09 | CI/CD and rollback | Blocked on CI/CD approval, P1 | PR checks, automatic dev deploy, manual production gate and rollback evidence | [#5](https://github.com/Wali-Mohamed/arabic-apparel-and-stickers/issues/5) |
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
