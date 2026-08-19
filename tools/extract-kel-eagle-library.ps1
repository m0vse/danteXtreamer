param(
    [string]$SourceSchematic = 'C:\Users\phil.taylor\source\repos\audioxtreamer\Pcb\AudioXtreamer_Ymh01x.sch',
    [string]$OutputLibrary = ''
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($OutputLibrary)) {
    $OutputLibrary = Join-Path $root 'hardware\easyeda\library-import\KEL_8831E-100-170L.lbr'
}

if (-not (Test-Path -LiteralPath $SourceSchematic)) {
    throw "AudioXtreamer Eagle schematic not found: $SourceSchematic"
}

$source = New-Object System.Xml.XmlDocument
$source.PreserveWhitespace = $false
$source.Load($SourceSchematic)

$kel = $source.SelectSingleNode('/eagle/drawing/schematic/libraries/library[@name="KEL"]')
if ($null -eq $kel) { throw 'The KEL library was not found in the source schematic.' }
if ($null -eq $kel.SelectSingleNode('devicesets/deviceset[@name="8831E-100-170L"]')) {
    throw 'The expected 8831E-100-170L device set was not found in the KEL library.'
}
if ($null -eq $kel.SelectSingleNode('packages/package[@name="KEL_8831E-100-170L"]')) {
    throw 'The expected KEL_8831E-100-170L footprint was not found in the KEL library.'
}
$gateCount = $kel.SelectNodes('devicesets/deviceset[@name="8831E-100-170L"]/gates/gate').Count
$connectionCount = $kel.SelectNodes('devicesets/deviceset[@name="8831E-100-170L"]/devices/device/connects/connect').Count
if ($gateCount -ne 2) { throw "Expected 2 symbol gates, found $gateCount." }
if ($connectionCount -ne 102) { throw "Expected 102 pin/pad mappings, found $connectionCount." }

$target = New-Object System.Xml.XmlDocument
$declaration = $target.CreateXmlDeclaration('1.0', 'utf-8', $null)
[void]$target.AppendChild($declaration)
$doctype = $target.CreateDocumentType('eagle', $null, 'eagle.dtd', $null)
[void]$target.AppendChild($doctype)
$eagle = $target.CreateElement('eagle')
$eagle.SetAttribute('version', $source.DocumentElement.GetAttribute('version'))
[void]$target.AppendChild($eagle)
$drawing = $target.CreateElement('drawing')
[void]$eagle.AppendChild($drawing)

foreach ($nodeName in @('settings', 'grid', 'layers')) {
    $node = $source.SelectSingleNode("/eagle/drawing/$nodeName")
    if ($null -ne $node) { [void]$drawing.AppendChild($target.ImportNode($node, $true)) }
}
[void]$drawing.AppendChild($target.ImportNode($kel, $true))

$directory = Split-Path -Parent $OutputLibrary
New-Item -ItemType Directory -Path $directory -Force | Out-Null
$settings = New-Object System.Xml.XmlWriterSettings
$settings.Indent = $true
$settings.Encoding = New-Object System.Text.UTF8Encoding($false)
$settings.NewLineChars = "`n"
$settings.NewLineHandling = [System.Xml.NewLineHandling]::Replace
$writer = [System.Xml.XmlWriter]::Create($OutputLibrary, $settings)
try { $target.Save($writer) } finally { $writer.Dispose() }
$libraryText = [System.IO.File]::ReadAllText($OutputLibrary)
$libraryText = $libraryText.Replace('<!DOCTYPE eagle PUBLIC "" "eagle.dtd"[]>', '<!DOCTYPE eagle SYSTEM "eagle.dtd">')
[System.IO.File]::WriteAllText($OutputLibrary, $libraryText, (New-Object System.Text.UTF8Encoding($false)))

$hash = (Get-FileHash -LiteralPath $OutputLibrary -Algorithm SHA256).Hash
Write-Host "Extracted EasyEDA-importable Eagle library: $OutputLibrary"
Write-Host "Verified: $gateCount gates, $connectionCount pin/pad mappings"
Write-Host "SHA-256: $hash"
