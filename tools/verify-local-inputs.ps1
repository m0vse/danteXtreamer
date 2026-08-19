[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$expectedInputs = @(
    [pscustomobject]@{
        Path = 'a203\hm-a203-en.pdf'
        Sha256 = '19C275980A53EBDB254BAB40AD25CAA34AB514D598365CA58C8A0BDDA8D8D8C3'
    }
    [pscustomobject]@{
        Path = 'a203\BF01_InterConn.rar'
        Sha256 = '6FBDD7C931506488961F8DC1B3D1D461321C79A0AD20CDD5C1BE53F807737B06'
    }
    [pscustomobject]@{
        Path = 'a203\SerialPortDemo.rar'
        Sha256 = '70E7F49B6A5C15A7FAA2561036ECCE08BCF84D614540B7AF36417C588BDA9B31'
    }
)

$failed = $false

foreach ($input in $expectedInputs) {
    $fullPath = Join-Path $repositoryRoot $input.Path
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        Write-Error "Missing local input: $($input.Path)" -ErrorAction Continue
        $failed = $true
        continue
    }

    $actual = (Get-FileHash -LiteralPath $fullPath -Algorithm SHA256).Hash
    if ($actual -ne $input.Sha256) {
        Write-Error "Hash mismatch: $($input.Path)" -ErrorAction Continue
        Write-Host "  expected: $($input.Sha256)"
        Write-Host "  actual:   $actual"
        $failed = $true
        continue
    }

    Write-Host "OK  $($input.Path)"
}

if ($failed) {
    exit 1
}

Write-Host 'All reviewed local inputs match.'
