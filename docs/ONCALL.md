# Local AI on-call responder (Issue #8)

This optional demonstration is local only. It cannot operate on Vercel or Neon.
The worker uses a real local Ollama model to choose between one predefined
remediation and escalation after gathering actual monitoring evidence. No paid
API or AI service account is required. Actual execution results are recorded
below and in [the task tracker](TASK_TRACKER.md); tests with mocked decisions
are not evidence of a successful real-model incident.

## Setup and reproduction

Install Docker Desktop with Linux containers and Docker Compose, then run from
the repository root in PowerShell:

```powershell
.\scripts\test-oncall.ps1
# Preserve the isolated stack after the outcome for inspection:
.\scripts\test-oncall.ps1 -KeepStack
# Alternative loopback ports if the defaults are occupied:
.\scripts\test-oncall.ps1 -GrafanaPort 3021 -FrontendPort 18201 -KeepStack
```

No Windows Ollama installation is needed: the script pulls `ollama/ollama:0.6.8`
and `qwen2.5:0.5b` into a project-specific model volume. Ollama's container runs
locally on Docker Desktop; its API has no published host port. The model is
about 398 MB; the runtime image download is substantially larger. Allow several
GB of free disk and several minutes for first setup. The available validation
machine has approximately 8 GB Docker RAM and 4 CPUs; GPU acceleration is not
required. Runtime memory and inference reliability must be assessed from the
actual demonstration, not inferred from model size. Offline use requires images
and the model to have been downloaded first.

The runtime image is pinned to digest
`sha256:50ab2378567a62b811a2967759dd91f254864c3495cbe50576bd8a85bc6edd56`.
The 494M Q4_K_M model is pinned by an explicit runtime digest check:
`a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`.
A changed registry tag causes a safe failure rather than silently testing a
different model. The demonstration records the reported runtime version/digest.

Reference: [Qwen2.5 0.5B model](https://ollama.com/library/qwen2.5:0.5b) and
[Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs).

The model-download service alone uses a bootstrap network with internet access.
It exits before runtime startup. Runtime services share an **internal Docker
network** without external egress. Grafana and the frontend publish only on
loopback (default ports 3020 and 18200). No existing database volume is mounted.
Do not merge the overlay into developer or production Compose projects.

The wrapper prints its unique `apparel-oncall-...` project name. It creates an
ephemeral random webhook secret and generated Grafana provisioning beneath
`.oncall-local/PROJECT/`, which Git ignores. Never publish that entire folder:
`secret` and `alerting.yaml` contain authentication material. Only the sanitized
`transcript.json` and `outcome.txt` are review evidence. The SQLite ledger lives
on a disposable tmpfs volume and disappears when its containers are removed.
The model cache volume remains; no existing volumes are deleted by this script.

## Architecture and permission boundaries

Grafana's real PricingUnavailable firing webhook authenticates to the oncall
service, which validates and sanitizes the payload, deduplicates by fingerprint
and incident start, and starts a single worker automatically. It does not poll
for fabricated alerts or rely on the test driver to invoke the agent.

The bounded state machine is Received -> Investigating -> Decision ->
Remediating -> Verifying -> Recovered, with Escalated as the failure exit.
SQLite records safe transition timestamps and tool results. Existing unfinished
incidents become Escalated after a worker restart; mutations are never replayed.
Another concurrent incident escalates rather than spawning another responder.

Diagnostic tools are fixed Python functions, not model-generated commands:

| Tool | Fixed operation |
| --- | --- |
| inspect_pricing_metrics | Read fixed pricing 5xx increase and sample freshness queries from Prometheus |
| inspect_failed_pricing_trace | Read recent Loki pricing 503 records and verify a corresponding Tempo request trace ID and HTTP status |
| probe_pricing | Quote one synthetic predefined Arabic product configuration; never submit orders |
| inspect_local_fault | Check the fixed marker and disposable-backend attestation |
| clear_local_pricing_fault | Remove only `/oncall-fault/pricing-unavailable` after all gates pass |
| escalate | Record a safe local stop state |

Diagnostics run in a fixed order. The real LLM receives only these sanitized
results and returns schema-constrained `action`/`reason` enums. Python validates
the exact response and independently enforces the permission gate. This is a
bounded decision agent, not an unrestricted general-purpose operations agent.
There is no deterministic fallback that impersonates a model decision.

Remediation requires current failures >=5, fresh successful diagnostics, a
matching 503 log/trace, a current 503 probe, an existing nonsymlink marker, a
healthy firing alert matching the incident fingerprint/start, and local arming.
Evidence expires after 30 seconds; metrics older than 15 seconds are rejected.
Logs are selected from the last 90 seconds. Slow inference can therefore safely
escalate even within its inference timeout.

The backend alone verifies the exact disposable database identity using the
existing fault guard, then writes a per-run attestation derived from the local
secret into the dedicated fault volume. The responder requires this attestation,
LOCAL_ONCALL=1 and absence of VERCEL/CI/integration/DATABASE_URL settings. The
responder receives no database credentials. The original marker path is retained
outside LOCAL_ONCALL mode; `scripts/test-alerting.ps1` is unchanged.

The responder has no Docker socket, GitHub token, production credentials or
host-source mounts. Only the fault volume, disposable ledger and read-only secret
are mounted. Its root filesystem is read-only; Linux capabilities are dropped.
Diagnostic HTTP destinations and queries are fixed in code; redirects are
rejected. The local Grafana demo credential is used only by fixed read operations
and is never passed to the model or transcript. This local credential is not a
production authorization design.

## Authentication, privacy and limits

- Grafana sends an ephemeral Bearer token; constant-time comparison precedes
  notification parsing. Incident inspection also requires this token.
- Reject unexpected alert/environment, invalid state/fingerprint, malformed or
  timezone-free timestamps, future/stale starts, payloads >64 KB and batches
  >10 alerts. Incident starts must be no older than ten minutes.
- Ignore annotations, alert text, arbitrary URLs, bodies, labels and telemetry
  instructions. Return only typed, allowlisted evidence to the model. Store no
  customer names, personalization, credentials, SQL parameters or raw exceptions.
- At most eight tools and one remediation attempt per incident; the successful
  path uses seven tools. Fixed HTTP calls time out after five seconds; model
  inference after at most 90 seconds. The incident deadline is ten minutes.
- Monitor-state polling is bounded recovery verification, not an open-ended
  model tool loop. It requires healthy Normal **and** a matching resolved webhook.
  Grafana KeepLast/Error/NoData is not accepted as recovery.
- Escalation records a local stop. It sends no messages to external services.
  Deployment, CI changes, filesystem exploration and destructive operations are
  unavailable tools and still require separate owner approval.

## Proof that the agent fixed the fault

The separate oncall driver first requires healthy pricing and Normal. It creates
the controlled marker and emits real pricing requests until the real Grafana
alert fires. The worker investigates metrics/logs/traces and invokes Ollama.
Only its allowed remediation removes the marker during normal execution.

The driver requires a model-decision audit record, successful removal tool,
repeated HTTP 200 quotes, healthy Normal, matching resolved receipt and Recovered
state before reporting PASSED. The wrapper writes the outcome **before** fallback
cleanup. Cleanup after failure cannot satisfy those assertions. No metrics,
traces, notifications or alert states are inserted artificially.

For a retained stack, set ONCALL_RUNTIME_DIR to its ignored absolute runtime
folder and use the same ports before running Compose inspection commands. Never
run `compose config` without `--quiet` because generated provisioning contains a
secret. To stop only that project:

```powershell
$env:ONCALL_RUNTIME_DIR=(Resolve-Path '.oncall-local/PROJECT').Path.Replace('\','/')
docker compose -p PROJECT -f compose.observability.yml -f compose.oncall.yml down
```

No `down -v`, schema changes, database reset or hosted configuration is needed.

## Validation and grading evidence

Deterministic tests cover authentication, validation, privacy, deduplication,
restart safety, production guards, stale/contradictory evidence, arbitrary model
output, single remediation, tool budgets, model/datasource failure and recovery.
Run them with the existing backend suite and isolated PostgreSQL integration:

```powershell
docker compose -p apparel-oncall-tests -f compose.ci.yml run --build --rm backend
docker compose -p apparel-oncall-tests -f compose.ci.yml run --build --rm frontend
docker compose -p apparel-oncall-tests -f compose.ci.yml down
```

## Observed real-model results - 2026-10-27

The full wrapper returned exit 0 / PASSED for isolated project
`apparel-oncall-5a385a1757`. Ollama 0.6.8 invoked the pinned Qwen2.5 0.5B model
above. The agent actually queried Prometheus, Loki and Tempo, probed pricing,
and independently removed the marker. No driver cleanup ran before success.

| Observation | UTC timestamp |
| --- | --- |
| Authenticated firing received / agent activated | 16:45:10.045527 |
| Real model chose clear_local_pricing_fault (16 output tokens) | 16:45:22.173844 |
| Agent removed marker, attempt 1 | 16:45:22.316141 |
| First verified HTTP 200 pricing probe | 16:45:22.425093 |
| Second verified HTTP 200 pricing probe | 16:45:24.516684 |
| Matching resolved webhook received | 16:47:30.460899 |
| Healthy Normal + resolved receipt accepted; Recovered | 16:47:31.544243 |

The incident fingerprint was `104cd504dd74996e`, start
`2026-10-27T16:45:10+00:00`. Actual failed-request trace:
`37b0e3c89638e031627253e097e736ea`. Seven tools were used, with one remediation;
the driver observed 27 real 503 responses. The successful transcript is preserved
at [observability/oncall-transcript.json](../observability/oncall-transcript.json).
These records reflect the executed source snapshot; subsequent audit-only
additions also record baseline/recovery timestamps and explicit firing state.

The first attempt **failed safely**: project `apparel-oncall-3debcca40d` received
the real firing alert, collected all four diagnostics, and invoked Ollama, but
the tiny model selected escalation despite sufficient evidence. It made no
remediation attempt. The wrapper recorded FAILED before fallback cleanup.
The [failed transcript](../observability/oncall-failed-attempt.json) is retained.
The model input was then reduced to compact typed facts with explicit decision
instructions; the same model and unchanged deterministic gates passed the retry.
This is not evidence of general incident-diagnosis reliability.

Validation: 93 backend tests including isolated PostgreSQL integration passed;
the final responder-only rerun passed 36 tests. Eight frontend tests, npm ci
(zero reported vulnerabilities), production build, Compose and PowerShell syntax,
documentation links and whitespace checks passed. One existing AnyIO deprecation
warning remains. No tests or failures were bypassed. Both real-demo stacks and
the test database were cleaned with plain down; no existing volumes were deleted.

The implemented local demonstration supports the rubric's two-point behavior;
it is not an awarded score or a claim of independent review. Publication was
authorized after revalidation. Issue #8 records the implementation handoff,
publication commit and CI results.
Manual Grafana screenshots and independent reviewer validation remain separate
requirements. A small model can make the wrong decision; the gate prevents
unsafe action but does not guarantee successful remediation. This demo repairs
only the injected marker fault, not unknown application or production incidents.
