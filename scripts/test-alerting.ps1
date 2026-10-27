param([int]$GrafanaPort = 3010, [int]$FrontendPort = 18100, [switch]$KeepStack)
$ErrorActionPreference = 'Stop'
$project = 'apparel-alert-' + [guid]::NewGuid().ToString('N').Substring(0, 10)
$previousGrafana = $env:LOCAL_GRAFANA_PORT
$previousFrontend = $env:LOCAL_FRONTEND_PORT
$env:LOCAL_GRAFANA_PORT = [string]$GrafanaPort
$env:LOCAL_FRONTEND_PORT = [string]$FrontendPort
$driverStarted = $false
function Stack {
    & docker compose -p $project -f compose.observability.yml -f compose.alerting.yml @args
    if ($LASTEXITCODE -ne 0) { throw "Local alert verification command failed (exit $LASTEXITCODE)" }
}
try {
    Write-Output "Isolated project: $project"
    Stack up -d --build frontend lgtm alert-receiver
    $driverStarted = $true
    Stack exec -T backend python /app/alerting_demo.py
    Stack --profile demo run --build --rm --no-deps browser
} finally {
    # Cleanup runs even if verification raises; no existing database volumes involved.
    $cleaned = $true
    if ($driverStarted) {
        & docker compose -p $project -f compose.observability.yml -f compose.alerting.yml exec -T backend python /app/alerting_demo.py --cleanup
        $cleaned = $LASTEXITCODE -eq 0
    }
    if (-not $KeepStack) {
        & docker compose -p $project -f compose.observability.yml -f compose.alerting.yml down
    } else {
        Write-Output "Retained local Grafana: http://localhost:$GrafanaPort (project $project); marker cleanup verified: $cleaned"
    }
    $env:LOCAL_GRAFANA_PORT = $previousGrafana
    $env:LOCAL_FRONTEND_PORT = $previousFrontend
    if (-not $cleaned) { throw 'Local fault cleanup could not be verified; inspect the retained project' }
}
