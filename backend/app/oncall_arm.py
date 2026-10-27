"""Backend-only attestation after verifying the disposable DB identity."""
import hashlib
import os
from pathlib import Path
from app.local_faults import local_fault_allowed

if __name__ == "__main__":
    if os.getenv("LOCAL_ONCALL") != "1" or not local_fault_allowed():
        raise SystemExit("Not an isolated on-call backend")
    Path("/oncall-fault/armed").write_text(hashlib.sha256(Path("/run/secrets/oncall").read_bytes()).hexdigest())
