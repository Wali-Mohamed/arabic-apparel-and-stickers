"""Pricing fault available only in the explicitly armed disposable demo stack."""
import os
from pathlib import Path
from collections.abc import Mapping
from contextlib import contextmanager

from fastapi import HTTPException
from app.db_config import database_url

PRICING_MARKER = Path("/tmp/apparel-pricing-unavailable")


def local_fault_allowed(settings: Mapping[str, str] | None = None) -> bool:
    env = os.environ if settings is None else settings
    if (env.get("LOCAL_PRICE_FAULTS") != "1" or env.get("LOCAL_OBSERVABILITY") != "1"
            or env.get("VERCEL") or env.get("CI")
            or env.get("RUN_POSTGRES_INTEGRATION") == "1"):
        return False
    try:
        url = database_url(env=env)
        return url.host == "postgres" and url.database == "apparel_observability" and url.username == "demo"
    except Exception:
        return False


def reject_unavailable_pricing() -> None:
    if local_fault_allowed() and PRICING_MARKER.is_file():
        raise HTTPException(status_code=503, detail="Pricing temporarily unavailable (local demo).")


@contextmanager
def pricing_fault():
    if not local_fault_allowed() or PRICING_MARKER.exists():
        raise RuntimeError("Fault requires a fresh explicitly armed local demo")
    try:
        PRICING_MARKER.touch()
        yield
    finally:
        PRICING_MARKER.unlink(missing_ok=True)
