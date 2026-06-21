# Load .env file into environment and run a worker
param(
    [string]$EnvFile = ".env",
    [string]$WorkerModule = "app.workers.plagiarism_worker"
)

if (-not (Test-Path $EnvFile)) {
    Write-Error "Env file '$EnvFile' not found in $(Get-Location)"
    exit 2
}

Get-Content $EnvFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -eq "" -or $line.StartsWith("#")) { return }
    if ($line -notmatch "^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$") { return }
    $k = $matches[1]
    $v = $matches[2]
    # Remove surrounding quotes if present
    if ($v.StartsWith('"') -and $v.EndsWith('"')) { $v = $v.Substring(1,$v.Length-2) }
    if ($v.StartsWith("'") -and $v.EndsWith("'")) { $v = $v.Substring(1,$v.Length-2) }
    Set-Item -Path Env:\$k -Value $v
}

if (-not $env:SUPABASE_URL -or -not $env:SUPABASE_SERVICE_ROLE_KEY) {
    Write-Host "WARNING: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set. Worker may run in local fallback mode."
}

Write-Host "Running worker module: $WorkerModule"
python -m $WorkerModule
