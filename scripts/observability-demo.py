"""Run only inside compose.observability.yml's disposable demo service."""
import json
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError


def request(url, data=None):
    body = json.dumps(data).encode() if data is not None else None
    with urllib.request.urlopen(urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json", "Accept": "application/json"}), timeout=10) as response:
        return json.load(response)


base = "http://backend:8000"
started_ns = time.time_ns()
products = request(base + "/api/products")
assert len(products) == 8
product = next(p for p in products if p["slug"] == "personalized-arabic-rectangular-tag")
options = {"text": "\u0633\u0644\u0627\u0645", "font": "Amiri"}
quote = request(base + f'/api/products/{product["id"]}/price', {"options": options, "quantity": 1})
assert quote["total_price_pence"] == 1200
order = request(base + "/api/orders", {"product_id": product["id"], "options": options,
    "quantity": 1, "customer_name": "LOCAL_PRIVATE_SENTINEL",
    "customer_contact": "LOCAL_PRIVATE_SENTINEL@example.invalid"})
assert order["status"] == "new" and order["total_price_pence"] == 1200
try:
    request(base + f'/api/products/{product["id"]}/price', {"options": {"text": "PRIVATE_INVALID_SENTINEL"}})
    raise AssertionError("Expected validation rejection")
except HTTPError as error:
    assert error.code == 422

# Query stored signals through Grafana datasource proxy, not the SDK exporter.
grafana = "http://lgtm:3000/api/datasources/proxy/uid/"
def query(source, endpoint, parameters):
    return request(grafana + source + endpoint + "?" + urllib.parse.urlencode(parameters))

for attempt in range(90):
    try:
        metrics = query("apparel-prometheus", "/api/v1/query", {"query": "apparel_requests_total"})
        assert metrics["data"]["result"]
        errors = query("apparel-prometheus", "/api/v1/query", {"query": "apparel_errors_total"})
        assert any(r["metric"].get("status") == "422" for r in errors["data"]["result"])
        logs = query("apparel-loki", "/loki/api/v1/query_range", {
            "query": '{service_name="arabic-apparel-api"}', "limit": 500,
            "start": str(started_ns), "end": str(time.time_ns())})
        entries = [json.loads(value[1]) for stream in logs["data"]["result"] for value in stream["values"]]
        entry = next(e for e in entries if e["route"] == "/api/orders" and e["status"] == "201")
        trace = request(grafana + "apparel-tempo/api/traces/" + entry["trace_id"])
        serialized = json.dumps(trace) + json.dumps(logs) + json.dumps(metrics)
        assert "LOCAL_PRIVATE_SENTINEL" not in serialized and "PRIVATE_INVALID_SENTINEL" not in serialized
        assert options["text"] not in serialized and json.dumps(options["text"])[1:-1] not in serialized
        assert "order.create" in json.dumps(trace)
        assert entry["span_id"]  # Exact trace-ID lookup links stored log -> trace.
        print("PASS: catalogue/Arabic quote/order/422; stored metrics, logs and matching trace")
        print("Order trace ID (sanitized): " + entry["trace_id"])
        exemplars = query("apparel-prometheus", "/api/v1/query_exemplars", {
            "query": "apparel_request_duration_seconds_bucket",
            "start": time.time() - 900, "end": time.time()})
        fresh_traces = {e["trace_id"] for e in entries}
        samples = [e for series in exemplars.get("data", []) for e in series.get("exemplars", [])
                   if e["labels"].get("trace_id") in fresh_traces]
        print("Stored metric exemplars: " + str(len(samples)))
        # Report, do not invent or silently equate ingestion with rendered UI.
        if samples:
            trace_id = samples[0]["labels"].get("trace_id")
            assert trace_id
            request(grafana + "apparel-tempo/api/traces/" + trace_id)
            print("PASS: stored exemplar resolves to a retained trace")
        else:
            print("GAP: no stored metric exemplar observed")
        break
    except (AssertionError, StopIteration, KeyError, HTTPError, URLError):
        if attempt == 89:
            raise RuntimeError("Stored telemetry verification timed out") from None
        time.sleep(2)
