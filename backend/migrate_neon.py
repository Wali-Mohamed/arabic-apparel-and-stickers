"""Explicit operator tool. Default mode validates locally; it never connects."""
import argparse
import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

from app.db_config import database_url


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Connect and apply migrations; requires separate approval")
    parser.add_argument("--expected-host")
    parser.add_argument("--expected-database")
    args = parser.parse_args(argv)
    try:
        if not os.getenv("MIGRATION_DATABASE_URL"):
            raise ValueError("Direct migration connection is required")
        url = database_url(migration=True)
        if url.query.get("sslmode") not in {"require", "verify-ca", "verify-full"}:
            raise ValueError("Migration connection must explicitly require SSL")
        config = Config(str(Path(__file__).resolve().parent / "alembic.ini"))
        head = ScriptDirectory.from_config(config).get_current_head()
        if not args.apply:
            print(f"Configuration validated; migration head {head}. No connection or migration performed.")
            return 0
        if not args.expected_host or not args.expected_database:
            raise ValueError("Explicit target confirmation is required")
        if (args.expected_host, args.expected_database) != (url.host, url.database):
            raise ValueError("Target confirmation does not match")
        engine = create_engine(url, poolclass=NullPool, hide_parameters=True, connect_args={"connect_timeout": 10})
        try:
            with engine.connect() as connection:
                # Direct connection holds a session lock across migration commits.
                # Only one invocation of this helper may migrate at a time.
                lock_key = 731204019
                locked = connection.scalar(text("SELECT pg_try_advisory_lock(:key)"), {"key": lock_key})
                connection.commit()
                if not locked:
                    raise RuntimeError("Another migration operator holds the lock")
                try:
                    config.attributes["connection"] = connection
                    command.upgrade(config, "head")
                    if MigrationContext.configure(connection).get_current_revision() != head:
                        raise RuntimeError("Migration head verification failed")
                    # Seed data is part of the existing versioned revisions;
                    # never rerun a separate seed/reset script against orders.
                    if connection.scalar(text("SELECT count(*) FROM products")) != 8:
                        raise RuntimeError("Catalogue seed verification failed")
                    if connection.scalar(text("SELECT count(*) FROM product_prices")) != 10:
                        raise RuntimeError("Price seed verification failed")
                    print(f"Migration/seed verification passed at {head}.")
                finally:
                    connection.rollback()
                    connection.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": lock_key})
                    connection.commit()
        finally:
            engine.dispose()
        return 0
    except Exception:
        # Driver/migration exceptions can contain URLs or SQL parameters. Fail
        # without dumping credentials or customer data to a shared console.
        print("Migration preparation/application failed; check target, SSL and configuration. No credentials printed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
