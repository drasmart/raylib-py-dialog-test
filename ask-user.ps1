<#
.SYNOPSIS
  Shows the raylib input dialog and returns its JSON response on stdout,
  the way an AI agent would call it as a tool.
.EXAMPLE
  .\ask-user.ps1 -Prompt "What is your name?"
  .\ask-user.ps1 "Project name?" -Default "demo" | ConvertFrom-Json
#>
param(
    [Parameter(Mandatory, Position = 0)][string]$Prompt,
    [string]$Default = ""
)

$root = $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Output (@{ status = "error"; error = "venv not found; run: python -m venv .venv; .venv\Scripts\pip install -r requirements.txt" } | ConvertTo-Json -Compress)
    exit 2
}

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
# raylib prints a "RAYLIB ... LOADED" banner to stderr on import; drop only that line.
$output = & $python (Join-Path $root "main.py") --prompt $Prompt --default $Default 2>&1 |
    Where-Object { "$_" -notmatch '^RAYLIB .* LOADED' }
$code = $LASTEXITCODE
Write-Output $output
exit $code
