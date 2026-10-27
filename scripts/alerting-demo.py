"""Executed inside the disposable backend by test-alerting.ps1. No order writes."""
import base64
from datetime import datetime, timezone
import json
import sys
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError

from app.local_faults import local_fault_allowed, pricing_fault, PRICING_MARKER

GRAFANA = "http://lgtm:3000"
API = "http://localhost:8000"
RECEIVER = "http://alert-receiver:8081"
TRANSITIONS = []
RUN_STARTED = datetime.now(timezone.utc)


def call(url, body=None, method=None):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if url.startswith(GRAFANA + "/"):
        # Public built-in local demo credentials only; never log headers/payload.
        headers["Authorization"] = "Basic " + base64.b64encode(b"admin:admin").decode()
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers, method=method), timeout=8) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        return error.code, None


def get(url):
    status, data = call(url)
    assert status == 200, "Local API unavailable"
    return data


def rule():
    data = get(GRAFANA + "/api/prometheus/grafana/api/v1/rules")
    rules = [r for g in data["data"]["groups"] for r in g["rules"] if r.get("name") == "PricingUnavailable"]
    assert len(rules) == 1, "Provisioned rule missing"
    item = rules[0]
    state = item.get("state", "unknown")
    health = item.get("health", "unknown")
    # KeepLast can report rule health=ok while Alertmanager records the error.
    active = get(GRAFANA + "/api/alertmanager/grafana/api/v2/alerts")
    for alert in active:
        if alert.get("labels", {}).get("alertname") == "PricingUnavailable":
            reason = alert.get("annotations", {}).get("grafana_state_reason", "")
            if "Error" in reason or "NoData" in reason or "No Data" in reason:
                health = "monitoring-unknown"
    key = (state, health)
    if not TRANSITIONS or TRANSITIONS[-1]["key"] != key:
        event = {"key": key, "state": state, "health": health,
                 "at": datetime.now(timezone.utc).isoformat()}
        TRANSITIONS.append(event)
        print(json.dumps({k: v for k, v in event.items() if k != "key"}), flush=True)
    return state, health


def wait_for(check, timeout=180):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            result = check()
            if result:
                return result
        except (AssertionError, KeyError, URLError):
            pass
        time.sleep(2)
    raise RuntimeError("Local alert verification timed out")


def events():
    return [e for e in get(RECEIVER + "/events")
            if datetime.fromisoformat(e["received_at"]) >= RUN_STARTED]


def assert_rule_contract():
    item = get(GRAFANA + "/api/v1/provisioning/alert-rules/pricing-unavailable")
    assert item["for"] == "30s"
    assert item["noDataState"] == item["execErrState"] == "KeepLast"
    a, b = item["data"]
    assert 'status=~"5.."' in a["model"]["expr"] and "[2m]" in a["model"]["expr"]
    assert b["model"]["expression"] == "$A >= 5"
    group = get(GRAFANA + "/api/v1/provisioning/folder/" + item["folderUID"] + "/rule-groups/" + item["ruleGroup"])
    assert group["interval"] == 10
    return a["model"]["expr"]


def main():
    assert local_fault_allowed(), "Never run this demonstration outside the armed disposable stack"
    if "--cleanup" in sys.argv:
        PRICING_MARKER.unlink(missing_ok=True)
        print("PASS: local fault marker absent")
        return
    wait_for(lambda: get(GRAFANA + "/api/health"))
    expression = assert_rule_contract()
    products = get(API + "/api/products")
    product = next(p for p in products if p["slug"] == "personalized-arabic-rectangular-tag")
    url = API + f'/api/products/{product["id"]}/price'
    valid = {"options": {"text": "\u0633\u0644\u0627\u0645", "font": "Amiri"}, "quantity": 1}
    def quote(expected=200, invalid=False):
        status, body = call(url, {"options": {"text": "INVALID_SENTINEL"}} if invalid else valid)
        assert status == expected, "Unexpected pricing HTTP status"
        if expected == 200:
            assert body["total_price_pence"] == 1200
        return True
    for _ in range(10):
        quote()
        time.sleep(2)
    def clean_baseline():
        query = urllib.parse.urlencode({"query": expression})
        metrics = get(GRAFANA + "/api/datasources/proxy/uid/apparel-prometheus/api/v1/query?" + query)
        points = metrics["data"]["result"]
        return rule() == ("inactive", "ok") and points and float(points[0]["value"][1]) == 0
    wait_for(clean_baseline)
    # A sustained stream of real 422 responses must never put this alert in Pending.
    for _ in range(20):
        quote(422, invalid=True)
        assert rule() == ("inactive", "ok")
        time.sleep(2)
    print("PASS: normal pricing and sustained 422 validation do not alert", flush=True)
    started_ns = time.time_ns()
    with pricing_fault():
        if "--fail-after-fault" in sys.argv:
            raise RuntimeError("Intentional cleanup verification")
        quote(422, invalid=True)  # Fault cannot replace normal validation.
        # Three failures must stay below threshold (allow several evaluations).
        for _ in range(3):
            quote(503)
            time.sleep(2)
        for _ in range(20):
            assert rule() == ("inactive", "ok")
            time.sleep(2)
        print("PASS: three failures remain below alert threshold", flush=True)
        pending_at = None
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            quote(503)
            state, health = rule()
            assert health == "ok"
            if state == "pending" and pending_at is None:
                pending_at = time.monotonic()
            if state == "firing":
                assert pending_at is not None and time.monotonic() - pending_at >= 25
                break
            time.sleep(2)
        else:
            raise RuntimeError("Alert did not fire")
        firing = wait_for(lambda: next((e for e in events() if e["state"] == "firing"), None))
        print("FIRING notification: " + json.dumps(firing), flush=True)
        # Real datasource query failure while firing: it must NOT resolve the alert.
        source = get(GRAFANA + "/api/datasources/uid/apparel-prometheus")
        changed = {k: source[k] for k in ("id", "uid", "name", "type", "access", "url", "jsonData") if k in source}
        source_changed = False
        try:
            status, _ = call(GRAFANA + "/api/datasources/uid/apparel-prometheus",
                             {**changed, "url": "http://127.0.0.1:1"}, method="PUT")
            assert status == 200, "Could not simulate local datasource outage"
            source_changed = True
            def failed_but_firing():
                quote(503)
                state, health = rule()
                if state == "inactive":
                    raise RuntimeError("Monitoring failure falsely resolved the alert")
                return health != "ok" and state == "firing"
            wait_for(failed_but_firing, timeout=120)
            assert not any(e["state"] == "resolved" and e["starts_at"] == firing["starts_at"] for e in events())
            print("PASS: datasource failure retained firing state; no false resolved delivery", flush=True)
        finally:
            if source_changed:
                status, _ = call(GRAFANA + "/api/datasources/uid/apparel-prometheus", changed, method="PUT")
                assert status == 200, "Restore the local datasource before continuing"
        wait_for(lambda: rule()[1] == "ok")
    assert not PRICING_MARKER.exists()
    quote()
    print("PASS: fault removed and pricing recovered to HTTP 200", flush=True)
    def recovered():
        quote()
        return rule() == ("inactive", "ok")
    wait_for(recovered, timeout=240)
    resolved = wait_for(lambda: next((e for e in events() if e["state"] == "resolved"
                                   and e["fingerprint"] == firing["fingerprint"]
                                   and e["starts_at"] == firing["starts_at"]), None))
    print("RESOLVED notification: " + json.dumps(resolved), flush=True)
    proxy = GRAFANA + "/api/datasources/proxy/uid/"
    def correlated():
        query = urllib.parse.urlencode({"query": '{service_name="arabic-apparel-api"}',
            "start": str(started_ns), "end": str(time.time_ns()), "limit": 1000})
        logs = get(proxy + "apparel-loki/loki/api/v1/query_range?" + query)
        records = [json.loads(v[1]) for stream in logs["data"]["result"] for v in stream["values"]]
        log = next(r for r in records if r["status"] == "503")
        trace = get(proxy + "apparel-tempo/api/traces/" + log["trace_id"])
        assert "pricing.request" in json.dumps(trace)
        print("PASS: failed pricing log resolves to trace " + log["trace_id"], flush=True)
        return True
    wait_for(correlated)
    assert "INVALID_SENTINEL" not in json.dumps(events())
    print("PASS: automatic Normal -> Pending -> Alerting -> Normal; firing/resolved webhook receipts", flush=True)


if __name__ == "__main__":
    try:
        main()
    finally:
        if local_fault_allowed():
            PRICING_MARKER.unlink(missing_ok=True)
