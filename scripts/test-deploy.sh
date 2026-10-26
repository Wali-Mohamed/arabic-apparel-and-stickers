#!/usr/bin/env bash
# Contract checks with fake tools: this never calls GitHub or a hosting provider.
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
test_dir=$(mktemp -d)
trap 'rm -rf -- "$test_dir"' EXIT
cat > "$test_dir/gh" <<'MOCK'
#!/usr/bin/env bash
if [[ "$1" == run ]]; then printf '%s\n' "${MOCK_CI_COUNT:-1}";
else printf '%s\n' "${MOCK_MAIN_SHA:-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa}"; fi
MOCK
cat > "$test_dir/jq" <<'MOCK'
#!/usr/bin/env bash
printf '%s\n' '{"mock":"payload"}'
MOCK
cat > "$test_dir/curl" <<'MOCK'
#!/usr/bin/env bash
printf '%s\n' called >> "$MOCK_CALL_LOG"
printf '%s' "${MOCK_HTTP_STATUS:-200}"
MOCK
chmod +x "$test_dir/gh" "$test_dir/jq" "$test_dir/curl"
export PATH="$test_dir:$PATH"
export MOCK_CALL_LOG="$test_dir/calls"
export GITHUB_REPOSITORY=example/test
export RELEASE_SHA=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
export DEPLOY_ENVIRONMENT=production
# Reserved invalid domain and fake token; curl is always mocked.
export DEPLOY_WEBHOOK_URL=https://adapter.invalid
export DEPLOY_WEBHOOK_TOKEN=synthetic-test-value
expect_failure() {
  if env "$@" bash "$script_dir/deploy.sh"; then
    echo 'Expected failure but deployment client succeeded' >&2; exit 1
  fi
}
expect_failure RELEASE_SHA=invalid
expect_failure DEPLOY_WEBHOOK_TOKEN=
expect_failure MOCK_CI_COUNT=0
expect_failure DEPLOY_ENVIRONMENT=development MOCK_MAIN_SHA=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
[[ ! -e "$MOCK_CALL_LOG" ]] || { echo 'Guard contacted adapter' >&2; exit 1; }
expect_failure MOCK_HTTP_STATUS=202
bash "$script_dir/deploy.sh"
env DEPLOY_ENVIRONMENT=development bash "$script_dir/deploy.sh"
# A previous tested SHA is accepted for production rollback even if main differs.
env MOCK_MAIN_SHA=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb bash "$script_dir/deploy.sh"
echo 'PASS: deployment guards, async rejection and mocked release/rollback requests'
