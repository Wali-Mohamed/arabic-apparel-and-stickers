"""Real local incident driver; normal flow NEVER removes the fault marker."""
import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import time
import urllib.request

from app.local_faults import local_fault_allowed, PRICING_MARKER
from app.oncall import Agent, MODEL, OLLAMA, alert_health, get

MODEL_DIGEST = 'a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67'


def snapshot():
    req = urllib.request.Request('http://oncall:8082/incidents', headers={
        'Authorization': 'Bearer ' + Path('/run/secrets/oncall').read_text()})
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.load(response)


def main():
    assert local_fault_allowed()
    if '--cleanup' in sys.argv:
        PRICING_MARKER.unlink(missing_ok=True)
        return
    result = {'model': MODEL, 'outcome': 'FAILED'}
    try:
        deadline = time.monotonic() + 120
        while True:
            try:
                tags = get(OLLAMA + '/api/tags')
                model = next(m for m in tags['models'] if m['name'] == MODEL)
                assert model['digest'] == MODEL_DIGEST, 'Untested model digest'
                result['model_digest'] = model['digest']
                result['ollama_version'] = get(OLLAMA + '/api/version')['version']
                snapshot()
                break
            except Exception:
                if time.monotonic() > deadline:
                    raise RuntimeError('Local model/worker unavailable')
                time.sleep(2)
        # Driver uses the fixed probe implementation, not an incident worker.
        class NoStore:
            pass
        probe = Agent(NoStore(), 'driver').probe_pricing
        for _ in range(15):
            assert probe()['status'] == 200
            time.sleep(2)
        deadline = time.monotonic() + 90
        while alert_health() != {'state': 'inactive', 'healthy': True}:
            if time.monotonic() > deadline:
                raise RuntimeError('Initial Normal not observed')
            probe()
            time.sleep(2)
        assert not PRICING_MARKER.exists()
        result['healthy_baseline_at'] = datetime.now(timezone.utc).isoformat()
        PRICING_MARKER.touch()
        result['fault_created_at'] = datetime.now(timezone.utc).isoformat()
        deadline = time.monotonic() + 600
        observed_failures = 0
        while time.monotonic() < deadline:
            status = probe()['status']
            if status == 503:
                observed_failures += 1
            else:
                assert status == 200
            data = snapshot()
            if any(i['state'] == 'Escalated' for i in data['incidents']):
                result.update(data)
                raise RuntimeError('Agent escalated; no success claimed')
            if any(i['state'] == 'Recovered' for i in data['incidents']):
                result.update(data)
                break
            time.sleep(2)
        else:
            result.update(snapshot())
            raise RuntimeError('Incident did not recover before deadline')
        assert observed_failures >= 5
        assert not PRICING_MARKER.exists(), 'Agent did not remove marker'
        events = [e['event'] for e in result['audit']]
        assert 'model.decision' in events and 'tool.clear_local_pricing_fault' in events
        assert any(e['event'] == 'model.decision' and e['detail']['eval_count'] > 0 for e in result['audit'])
        assert 'notification.resolved' in events and 'Recovered' in events
        for _ in range(3):
            assert probe()['status'] == 200
        assert alert_health() == {'state': 'inactive', 'healthy': True}
        result['observed_503_requests'] = observed_failures
        result['outcome'] = 'PASSED'
        result['recovery_verified_at'] = datetime.now(timezone.utc).isoformat()
    finally:
        # No cleanup here: wrapper records failure before any fallback unlink.
        print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
