[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$interfaceRoot = Join-Path $repositoryRoot 'hardware\interfaces'

$yamaha = Import-Csv (Join-Path $interfaceRoot 'yamaha-mln2-pin-matrix.csv')
$a203 = Import-Csv (Join-Path $interfaceRoot 'a203-pin-matrix.csv')
$fpga = Import-Csv (Join-Path $interfaceRoot 'fpga-pin-assignment.csv')

function Assert-SequentialPins {
    param(
        [object[]]$Rows,
        [string]$Column,
        [int]$Last,
        [string]$Name
    )

    $actual = @($Rows | ForEach-Object { [int]$_.$Column } | Sort-Object)
    $expected = @(1..$Last)
    if (Compare-Object $expected $actual) {
        throw "$Name must contain every numbered contact from 1 through $Last exactly once."
    }
}

Assert-SequentialPins -Rows $yamaha -Column 'contact' -Last 100 -Name 'Yamaha matrix'
Assert-SequentialPins -Rows $a203 -Column 'pin' -Last 124 -Name 'A203 matrix'

$duplicateBalls = @($fpga | Group-Object ball | Where-Object Count -gt 1)
if ($duplicateBalls) {
    throw "Duplicate FPGA balls: $($duplicateBalls.Name -join ', ')"
}

$duplicateSignals = @($fpga | Group-Object fpga_signal | Where-Object Count -gt 1)
if ($duplicateSignals) {
    throw "Duplicate FPGA signals: $($duplicateSignals.Name -join ', ')"
}

$bankCapacity = @{ '0' = 40; '1' = 50; '2' = 40; '3' = 56 }
foreach ($group in ($fpga | Group-Object bank)) {
    if (-not $bankCapacity.ContainsKey($group.Name)) {
        throw "Unexpected bank $($group.Name)."
    }
    if ($group.Count -gt $bankCapacity[$group.Name]) {
        throw "Bank $($group.Name) assigns $($group.Count) pins but has capacity $($bankCapacity[$group.Name])."
    }
    Write-Host "OK  bank $($group.Name): $($group.Count)/$($bankCapacity[$group.Name]) user I/O assigned"
}

$fpgaByBall = @{}
foreach ($row in $fpga) {
    $fpgaByBall[$row.ball] = $row
}

foreach ($matrix in @($yamaha, $a203)) {
    foreach ($row in $matrix) {
        if (-not $row.fpga_ball) {
            continue
        }
        if (-not $fpgaByBall.ContainsKey($row.fpga_ball)) {
            throw "Connector matrix references unassigned FPGA ball $($row.fpga_ball)."
        }
        if ($fpgaByBall[$row.fpga_ball].bank -ne $row.bank) {
            throw "Connector matrix bank mismatch at FPGA ball $($row.fpga_ball)."
        }
    }
}

Write-Host "OK  Yamaha contacts: $($yamaha.Count)/100"
Write-Host "OK  A203 contacts: $($a203.Count)/124"
Write-Host "OK  FPGA user I/O: $($fpga.Count)/186 with no duplicate balls or signals"
Write-Host 'Pin-matrix structural checks passed. Run ISE placement before schematic release.'
