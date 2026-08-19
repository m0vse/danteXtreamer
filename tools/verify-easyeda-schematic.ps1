$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$schematicPath = Join-Path $root 'hardware\easyeda\danteXtreamer_revA_preliminary.json'
$manifestPath = Join-Path $root 'hardware\easyeda\jlc-parts.csv'
$fpgaPath = Join-Path $root 'hardware\interfaces\fpga-pin-assignment.csv'
$yamahaPath = Join-Path $root 'hardware\interfaces\yamaha-mln2-pin-matrix.csv'
$a203Path = Join-Path $root 'hardware\interfaces\a203-pin-matrix.csv'

if (-not (Test-Path -LiteralPath $schematicPath)) { throw "Missing generated schematic: $schematicPath" }
if (-not (Test-Path -LiteralPath $manifestPath)) { throw "Missing JLC manifest: $manifestPath" }

$document = Get-Content -LiteralPath $schematicPath -Raw | ConvertFrom-Json
if ($document.docType -ne '5') { throw 'Expected EasyEDA multi-document docType 5.' }
if ($document.schematics.Count -ne 8) { throw "Expected 8 schematic sheets, found $($document.schematics.Count)." }

$allData = $document | ConvertTo-Json -Depth 10 -Compress
$requiredParts = @('C39313', 'C9926', 'C165948', 'C7519', 'C6478', 'C15643', 'C82344', 'C43590', 'C133191', 'C2149796', 'C181295')
foreach ($part in $requiredParts) {
    if ($allData -notmatch [regex]::Escape($part)) { throw "Required LCSC part $part is absent from the schematic." }
}

$fpgaRows = Import-Csv -LiteralPath $fpgaPath
foreach ($row in $fpgaRows) {
    if ($allData -notmatch [regex]::Escape($row.fpga_signal)) { throw "FPGA net missing from schematic: $($row.fpga_signal)" }
    if ($row.interface -ne 'board debug') {
        $labelPattern = '~' + [regex]::Escape($row.fpga_signal) + '~'
        $labelCount = [regex]::Matches($allData, $labelPattern).Count
        if ($labelCount -lt 2) { throw "Interface net is not labelled at both endpoints: $($row.fpga_signal) (count $labelCount)" }
    }
}

$yamahaRows = Import-Csv -LiteralPath $yamahaPath
$a203Rows = Import-Csv -LiteralPath $a203Path
if ($yamahaRows.Count -ne 100) { throw "Yamaha matrix does not contain 100 contacts." }
if ($a203Rows.Count -ne 124) { throw "A203 matrix does not contain 124 contacts." }

foreach ($sheet in $document.schematics) {
    $page = $sheet.dataStr | ConvertFrom-Json
    if ($page.head.docType -ne '1') { throw "Sheet $($sheet.title) is not an EasyEDA schematic page." }
    if ($page.shape.Count -eq 0) { throw "Sheet $($sheet.title) is empty." }
}

if ($allData -notmatch 'DNI/customer supplied') { throw 'Customer-supplied connector assembly note is missing.' }
if ($allData -notmatch 'ETHERNET PHY DESIGN HOLD') { throw 'Ethernet PHY design hold is missing.' }
if ($allData -notmatch 'NOT FABRICATION READY') { throw 'Preliminary-release warning is missing.' }

Write-Host "EasyEDA schematic validation passed: 8 sheets, $($fpgaRows.Count) FPGA assignments, 100 Yamaha contacts, 124 A203 contacts."
