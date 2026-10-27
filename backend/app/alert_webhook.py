"""Internal local-demo receiver: never persist or print raw webhook payloads."""
from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re
import threading

EVENTS = deque(maxlen=200)
LOCK = threading.Lock()


def timestamp(value):
    if not isinstance(value, str) or len(value) > 40:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.isoformat() if parsed.tzinfo else None
    except ValueError:
        return None


def sanitize(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("alerts"), list):
        return []
    safe = []
    for alert in payload["alerts"][:100]:
        if not isinstance(alert, dict) or not isinstance(alert.get("labels"), dict):
            continue
        fingerprint = alert.get("fingerprint", "")
        if (alert["labels"].get("alertname") != "PricingUnavailable"
                or alert.get("status") not in {"firing", "resolved"}
                or not isinstance(fingerprint, str)
                or not re.fullmatch(r"[a-fA-F0-9]{16,64}", fingerprint)):
            continue
        start, end = timestamp(alert.get("startsAt")), timestamp(alert.get("endsAt"))
        if start is None or end is None:
            continue
        safe.append({"alertname": "PricingUnavailable", "state": alert["status"],
                     "starts_at": start, "ends_at": end, "fingerprint": fingerprint})
    return safe


class Receiver(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # Includes raw URL otherwise.

    def reply(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            return self.reply(200, {"status": "ok"})
        if self.path == "/events":
            with LOCK:
                return self.reply(200, list(EVENTS))
        self.reply(404, {})

    def do_POST(self):
        if self.path != "/webhook":
            return self.reply(404, {})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 65536:
                return self.reply(413, {})
            records = sanitize(json.loads(self.rfile.read(size)))
        except (ValueError, TypeError):
            return self.reply(400, {})
        with LOCK:
            for record in records:
                if not any(all(e.get(k) == v for k, v in record.items()) for e in EVENTS):
                    record["received_at"] = datetime.now(timezone.utc).isoformat()
                    EVENTS.append(record)
        self.reply(202, {"accepted": len(records)})


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8081), Receiver).serve_forever()
