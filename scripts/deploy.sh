#!/usr/bin/env bash
set -euo pipefail
# Never enable xtrace: the environment contains hosting credentials.
[[ "${RELEASE_SHA:-}" =~ ^[0-9a-f]{40}$ ]] || { echo 'A full lowercase commit SHA is required.' >&2; exit 1; }
[[ "${DEPLOY_ENVIRONMENT:-}" == development || "${DEPLOY_ENVIRONMENT:-}" == production ]] || exit 1
[[ "${DEPLOY_WEBHOOK_URL:-}" == https://* && -n "${DEPLOY_WEBHOOK_TOKEN:-}" ]] || {
  echo 'Hosting adapter is not configured; no deployment attempted.' >&2; exit 1;
}
# Only revisions that passed this repository's main push CI can be released.
passed=$(gh run list --repo "$GITHUB_REPOSITORY" --workflow ci.yml --branch main \
  --event push --commit "$RELEASE_SHA" --status success --limit 1 --json databaseId --jq length)
[[ "$passed" == 1 ]] || { echo 'No successful main push CI for this revision.' >&2; exit 1; }
if [[ "$DEPLOY_ENVIRONMENT" == development ]]; then
  current=$(gh api "repos/$GITHUB_REPOSITORY/git/ref/heads/main" --jq .object.sha)
  [[ "$current" == "$RELEASE_SHA" ]] || { echo 'Superseded development revision; refusing stale deployment.' >&2; exit 1; }
fi
payload=$(jq -n --arg sha "$RELEASE_SHA" --arg environment "$DEPLOY_ENVIRONMENT" \
  '{sha: $sha, environment: $environment}')
# The adapter must return 200/204 ONLY after deployment and smoke checks complete.
# Suppress response bodies/errors that could contain credentials or customer data.
if ! status=$(curl --silent --fail --output /dev/null --write-out '%{http_code}' --connect-timeout 15 --max-time 600 \
  --header "Authorization: Bearer $DEPLOY_WEBHOOK_TOKEN" \
  --header 'Content-Type: application/json' --data "$payload" "$DEPLOY_WEBHOOK_URL"); then
  echo 'Deployment adapter failed or timed out; inspect restricted hosting logs.' >&2
  exit 1
fi
[[ "$status" == 200 || "$status" == 204 ]] || { echo 'Adapter did not confirm completed rollout (HTTP 200/204 required).' >&2; exit 1; }
echo "Deployment verified by adapter: $DEPLOY_ENVIRONMENT $RELEASE_SHA"
