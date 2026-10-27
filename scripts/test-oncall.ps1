param([int]$GrafanaPort=3020, [int]$FrontendPort=18200, [switch]$KeepStack)
$ErrorActionPreference='Stop'
$project='apparel-oncall-'+[guid]::NewGuid().ToString('N').Substring(0,10)
$prior=@($env:ONCALL_RUNTIME_DIR,$env:LOCAL_GRAFANA_PORT,$env:LOCAL_FRONTEND_PORT)
$runtime=Join-Path $PWD ".oncall-local/$project"
[void][IO.Directory]::CreateDirectory($runtime)
$env:ONCALL_RUNTIME_DIR=$runtime.Replace('\','/')
$env:LOCAL_GRAFANA_PORT=[string]$GrafanaPort
$env:LOCAL_FRONTEND_PORT=[string]$FrontendPort
$bytes=New-Object byte[] 32
$rng=[Security.Cryptography.RandomNumberGenerator]::Create()
$rng.GetBytes($bytes); $rng.Dispose()
$secret=[Convert]::ToBase64String($bytes)
[IO.File]::WriteAllText((Join-Path $runtime 'secret'),$secret,[Text.UTF8Encoding]::new($false))
$rule=[IO.File]::ReadAllText((Join-Path $PWD 'observability/alerting.yaml'))
$rule=$rule.Replace('http://alert-receiver:8081/webhook','http://oncall:8082/webhook')
$rule=$rule.Replace('httpMethod: POST',"httpMethod: POST`n          authorization_scheme: Bearer`n          authorization_credentials: '$secret'")
[IO.File]::WriteAllText((Join-Path $runtime 'alerting.yaml'),$rule,[Text.UTF8Encoding]::new($false))
$secret=$null
function Stack {
    & docker compose -p $project -f compose.observability.yml -f compose.oncall.yml @args
    if($LASTEXITCODE -ne 0){throw "On-call command failed (exit $LASTEXITCODE)"}
}
$outcome='FAILED'
try {
    Write-Output "Isolated on-call project: $project"
    Stack --profile setup run --rm model-download
    Stack up -d --build frontend oncall
    # Driver writes sanitized JSON only. A failing native command still fails this wrapper.
    Stack exec -T backend python /app/oncall_demo.py | Tee-Object -FilePath (Join-Path $runtime 'transcript.json')
    $outcome='PASSED'
} finally {
    $transcriptPath=Join-Path $runtime 'transcript.json'
    if(Test-Path -LiteralPath $transcriptPath){
        $transcriptText=[IO.File]::ReadAllText($transcriptPath)
        [IO.File]::WriteAllText($transcriptPath,$transcriptText,[Text.UTF8Encoding]::new($false))
    }
    [IO.File]::WriteAllText((Join-Path $runtime 'outcome.txt'),$outcome)
    Write-Output "Recorded demonstration outcome: $outcome; evidence: $runtime"
    # Outcome recorded FIRST. This fallback can never satisfy an agent assertion.
    & docker compose -p $project -f compose.observability.yml -f compose.oncall.yml exec -T backend python /app/oncall_demo.py --cleanup
    if(-not $KeepStack){
        & docker compose -p $project -f compose.observability.yml -f compose.oncall.yml down
    }
    $env:ONCALL_RUNTIME_DIR=$prior[0]
    $env:LOCAL_GRAFANA_PORT=$prior[1]
    $env:LOCAL_FRONTEND_PORT=$prior[2]
}
