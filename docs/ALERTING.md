# Local user-impact alerting (Issue #7)

This is a local demonstration, not Vercel/Neon production monitoring. It extends
the optional OpenTelemetry/Grafana LGTM stack with a real Grafana-managed alert
and an internal webhook receiver. No external notifications or AI agent run.

## Rule and runbook

`PricingUnavailable` uses the existing `apparel-prometheus` datasource and
`apparel_requests_total` for POST `/api/products/{product_id}/price` only.
`increase(...[2m])` counts 5xx responses; threshold is **>=5**, evaluated every
**10 seconds**, continuously breached for **30 seconds**. Normal 4xx/422 input
rejections are excluded. No keep-firing delay is added after recovery.

```promql
sum(increase(apparel_requests_total{route="/api/products/{product_id}/price",method="POST",status=~"5.."}[2m]))
or (0 * sum(increase(apparel_requests_total{route="/api/products/{product_id}/price",method="POST"}[2m])))
```

The zero fallback requires an existing pricing series. Both No Data and query
Error use Grafana's KeepLast handling: they retain prior alert state instead of
claiming successful recovery. Rule evaluation health must also be **ok** before
the verifier accepts Normal/recovery. Grafana can report rule health=ok under
KeepLast despite an evaluation error; the verifier also checks Alertmanager's
`grafana_state_reason` for Error/NoData and treats it as monitoring-unknown.
A healthy-looking retained state with bad
evaluation health is UNKNOWN, not evidence the application works. An idle/new
stack needs warm-up traffic. This alert detects failed responses, not a totally
dead application that emits no metrics; a separate availability/freshness alert
would be required for comprehensive production monitoring.

`environment=local-demo`, severity warning. Provisioning is mounted only by
`compose.alerting.yml`, never normal Compose/Vercel. The local-only notification
policy routes firing AND resolved notifications to
`http://alert-receiver:8081/webhook`. The receiver publishes no host port and
retains at most 200 in-memory sanitized events: alert name, state, timestamps,
fingerprint. It drops all other labels, annotations, URLs, bodies, contacts,
personalization and credentials. HTTP access logging is disabled. Notifications
are not durable across receiver recreation and this unauthenticated internal
receiver must not be exposed publicly or directly used as a privileged agent.

Diagnosis: confirm a real pricing 5xx increase, inspect the pricing log/trace,
and check rule evaluation health. Restore pricing availability first; do not
silence the alert, change its threshold or restart Grafana to demonstrate recovery.
After the last 503 ages out of the two-minute window, normal pricing traffic
should produce Normal and a resolved notification (plus export/evaluation delay).

## Reproduce (PowerShell, repository root)

```powershell
./scripts/test-alerting.ps1
# Keep the isolated stack afterward for manual UI inspection:
./scripts/test-alerting.ps1 -KeepStack
# Choose other free loopback ports if needed:
./scripts/test-alerting.ps1 -GrafanaPort 3011 -FrontendPort 18101 -KeepStack
# Process-scoped execution-policy alternative used for validation:
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/test-alerting.ps1
```

The wrapper prints a unique `apparel-alert-...` project name, builds the app,
starts the standalone observability + alerting files, and runs the verifier
inside that project's backend. Default Grafana is http://localhost:3010 and
the app is http://localhost:18100. Use only the local LGTM demonstration account;
never publish login details or expose this stack publicly.
Do not stop another existing stack to free ports. Allow several minutes for
startup, warm-up, threshold/pending, datasource outage and recovery verification.
After the API verification, the wrapper also runs a read-only Chromium check
that PricingUnavailable is visible in the actual Grafana Alert rules UI.

The verifier:

1. Reads back the provisioned threshold/window/30s pending/10s interval and warms
   up valid Arabic pricing. Requires Normal (`inactive`) with healthy evaluation.
2. Sends sustained 422 validation requests and checks they do not alert.
3. Arms the pricing marker, confirms three 503s remain below threshold, then
   sends enough real valid pricing requests to observe Pending then Alerting
   (`firing`). Confirms a safe firing webhook receipt.
4. Temporarily points ONLY this isolated Grafana datasource to an unreachable
   local port. Requires a query error while the alert remains firing and verifies
   no false resolved delivery. Restores the datasource in a finally block.
   This is a real query failure, not an inserted metric or forced alert state.
   The local Prometheus datasource is provisioned editable to permit this test;
   the endpoint is restored afterward. Loki/Tempo and production settings are
   not modified by the outage test.
5. Removes the marker, requires pricing HTTP 200, waits for healthy Normal and
   a matching resolved webhook fingerprint. Correlates a failed request's stored
   log with its Tempo trace. Prints sanitized timestamps/states/receipts only.

The driver never creates orders. Its valid pricing body is synthetic and is not
recorded in telemetry. It uses only fixed internal URLs and refuses to start
unless the local fault guards pass. PostgreSQL is a new tmpfs database in the
unique project; existing databases/volumes, prices/catalogue and migrations are
unchanged. Never merge these files into a live/developer project.

## Fault isolation and cleanup

The application checks all of: `LOCAL_PRICE_FAULTS=1`, `LOCAL_OBSERVABILITY=1`,
database host `postgres`, database `apparel_observability`, role `demo`, and
absence of VERCEL/CI/RUN_POSTGRES_INTEGRATION guards. Only the alerting overlay
sets LOCAL_PRICE_FAULTS. Normal development, application CI and Vercel cannot
activate it with a leftover marker. Tests explicitly simulate an isolated
configuration when checking the positive case.

The marker is `/tmp/apparel-pricing-unavailable`, inside the disposable backend.
The fault is checked after product/options/price validation and returns sanitized
503 without a write. There is no fault-control HTTP API. Python context/finally
cleanup removes the marker on ordinary verification exceptions; the PowerShell
wrapper also executes cleanup after driver failure. With -KeepStack the marker
must still be absent. Abrupt host power loss cannot execute finally blocks;
recreate the disposable stack or run explicit cleanup before reusing it.

For a retained stack, replace PROJECT with its printed name:

```powershell
$env:LOCAL_GRAFANA_PORT='3010'
$env:LOCAL_FRONTEND_PORT='18100'
docker compose -p PROJECT -f compose.observability.yml -f compose.alerting.yml exec -T backend python /app/alerting_demo.py --cleanup
docker compose -p PROJECT -f compose.observability.yml -f compose.alerting.yml down
```

Use the same port values selected for that run. No down -v, database reset,
schema downgrade or existing-file deletion is required.

## Tests and evidence

Backend pytest covers fault guards, marker recovery/exception cleanup and
webhook data minimization; existing telemetry tests cover exporter failure and
order persistence. The real Grafana script verifies threshold, pending duration,
4xx exclusion, datasource error retention, notifications and automatic recovery.
It checks live state rather than fabricating rule states or metrics. Prometheus
increase extrapolates, so short sparse bursts are approximate counts; the sustained
fault comfortably exceeds the threshold. A fresh project avoids old alert history.

For manual evidence, open Grafana > Alerting > Alert rules > PricingUnavailable
while the script runs. Capture Normal, Pending/Alerting with the query, and
recovered Normal with evaluation health. Capture sanitized firing/resolved
receiver output and one failed request's correlated log/trace. Record timestamps,
commands and the tested diff/commit; redact any account/credential details. These
manual screenshots and independent reviewer validation are distinct from API
state verification and must not be claimed without evidence. Actual observed
results and any failed attempts are recorded in TASK_TRACKER.md and Issue #7.

Future Issue #8 may consume the same sanitized webhook via an authenticated,
bounded responder with approved local diagnostic/remediation permissions; no
agent, external notification destination or production monitoring is implemented.

## Observed local validation - 2026-10-27

The final fresh-project PowerShell wrapper completed successfully, including
Chromium rule-detail visibility and automatic marker/container cleanup. All
times below are UTC (also London local time on this date):

| Observation | Time |
| --- | --- |
| Normal, healthy evaluation | 10:36:54.726077 |
| Pending, healthy evaluation | 10:38:40.497394 |
| Alerting observed | 10:39:11.745210 |
| Firing webhook received | 10:39:10.028921 |
| Firing retained during datasource error; monitoring unknown | 10:39:42.880977 |
| Datasource restored; pricing subsequently returned HTTP 200 | 10:40:11.723189 |
| Resolved webhook received | 10:41:40.652989 |
| Normal observed again, healthy evaluation | 10:41:42.439649 |

The firing/resolved events shared fingerprint `104cd504dd74996e` and incident
start `2026-10-27T10:39:10+00:00`. Failed pricing log -> retained trace:
`3577ac6348cbcfcb397701037a5bc938`. No orders were submitted by the alert driver.
Sustained 422s and three 503s stayed Normal; the sustained fault caused a real
pending/firing transition. The actual datasource outage retained firing and
produced no false resolved delivery. Exporter-failure regression tests also pass.

Final tests: 57 backend tests including real isolated PostgreSQL integration;
56 offline backend tests; eight frontend tests and production build passed.
One existing AnyIO deprecation warning remains. Initial failures were corrected
and rerun: a misplaced unit-test block, over-escaped Grafana expression, read-only
datasource blocking the outage test, KeepLast masking rule health, and collapsed
Grafana list controls. The UI verifier now uses the canonical rule detail page.
These earlier failures are not counted as successful validation.

No alert screenshots or independent human review have been captured. The API
state machine, notification delivery and Chromium rule-page presence are verified;
manual UI state-history screenshots remain a separate evidence task. Publication
was authorized after review; the runbook annotation targets this document on main.
Publication and CI results are recorded in Issue #7. No hosted monitoring is claimed.
The recorded trace ID and notifications belonged to the disposable run; reproduce
with fresh traffic/new IDs rather than expecting removed containers to retain them.
