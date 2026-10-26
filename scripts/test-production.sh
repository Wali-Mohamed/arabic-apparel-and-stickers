#!/usr/bin/env bash
# Local/CI only. All requests stay on this isolated project's Docker networks.
set -euo pipefail
export POSTGRES_DB=apparel_production_smoke
export POSTGRES_USER=smoke
export POSTGRES_PASSWORD='ci_%/@smoke_only'
export PUBLIC_ORIGIN=http://frontend:8080
export ALLOWED_HOSTS=frontend,localhost,127.0.0.1
export RELEASE_TAG=smoke
project="apparel-production-smoke-${GITHUB_RUN_ID:-local}-$$"
stack=(docker compose -p "$project" -f compose.production.yml -f compose.production-smoke.yml)
cleanup() { "${stack[@]}" down --remove-orphans; }
trap cleanup EXIT
"${stack[@]}" --profile smoke build
"${stack[@]}" up -d --wait --wait-timeout 180 frontend
for service in frontend backend postgres; do
  container=$("${stack[@]}" ps -q "$service")
  ports=$(docker inspect --format '{{json .HostConfig.PortBindings}}' "$container")
  [[ "$ports" == '{}' || "$ports" == null ]] || { echo 'Smoke service unexpectedly publishes a port' >&2; exit 1; }
done
database=$("${stack[@]}" ps -q postgres)
persistent=$(docker inspect --format '{{range .Mounts}}{{if eq .Type "volume"}}volume{{end}}{{end}}' "$database")
[[ -z "$persistent" ]] || { echo 'Smoke database unexpectedly mounts a persistent volume' >&2; exit 1; }
echo 'PASS: no public ports or persistent database mounts in smoke stack'
"${stack[@]}" run --rm --no-deps browser
# Verify the HTTP orders really committed into PostgreSQL from a new session.
"${stack[@]}" exec -T backend python -c '
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models import Order
with SessionLocal() as db:
    count = db.scalar(select(func.count()).select_from(Order).where(Order.customer_contact == "smoke@example.invalid", Order.status == "new"))
    assert count == 2, "Expected exactly two synthetic persisted demo orders"
print("PASS: two synthetic orders persisted in PostgreSQL")
'
# Restarting API must not lose persisted data or leave Nginx with a stale upstream.
"${stack[@]}" restart backend
"${stack[@]}" up -d --wait --wait-timeout 90 frontend
"${stack[@]}" exec -T backend python -c '
import urllib.request
from sqlalchemy import select, func
from app.database import SessionLocal
from app.models import Order
with SessionLocal() as db:
    assert db.scalar(select(func.count()).select_from(Order)) == 2
assert urllib.request.urlopen("http://frontend:8080/health/db", timeout=10).status == 200
print("PASS: persistence and reverse proxy after API restart")
'
