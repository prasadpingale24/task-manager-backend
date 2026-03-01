# PowerShell script to run tests locally with correct environment
# This script loads variables from .env and overrides them for local testing.

$envFile = ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^\s*([^#=]+)=(.+)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim().Trim("'").Trim('"')
            [System.Environment]::SetEnvironmentVariable($name, $value)
        }
    }
}

# Override for local testing (since Docker 'db' host isn't accessible from host)
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5433"
$env:POSTGRES_DB = "task_manager_test"
$env:SECRET_KEY = "test-secret-key"
$env:PYTHONPATH = $PSScriptRoot

Write-Host "Running tests with POSTGRES_HOST=$env:POSTGRES_HOST and POSTGRES_DB=$env:POSTGRES_DB..." -ForegroundColor Cyan

uv run pytest tests/ -v
