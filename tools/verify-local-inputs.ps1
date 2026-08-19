[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$expectedInputs = @(
    [pscustomobject]@{
        Path = 'vendor\audiocom\a203\hm-a203-en.pdf'
        Sha256 = '19C275980A53EBDB254BAB40AD25CAA34AB514D598365CA58C8A0BDDA8D8D8C3'
    }
    [pscustomobject]@{
        Path = 'vendor\audiocom\a203\BF01_InterConn.rar'
        Sha256 = '6FBDD7C931506488961F8DC1B3D1D461321C79A0AD20CDD5C1BE53F807737B06'
    }
    [pscustomobject]@{
        Path = 'vendor\audiocom\a203\SerialPortDemo.rar'
        Sha256 = '70E7F49B6A5C15A7FAA2561036ECCE08BCF84D614540B7AF36417C588BDA9B31'
    }
    [pscustomobject]@{
        Path = 'vendor\yamaha\01x\Yamaha-01X-Service-Manual.pdf'
        Sha256 = 'DD5769860153C6BACF693709EEC54E1BB4FACB24F76821A1CA0000F4A89166D0'
    }
    [pscustomobject]@{
        Path = 'vendor\yamaha\i88x\yamaha_i88x.pdf'
        Sha256 = '7D4F9FBCA94FA14F5DA5116900E5AC3F4A7E4CE7D44B542833891306F9AA1867'
    }
    [pscustomobject]@{
        Path = 'vendor\ztex\usb-fpga-2.01.pdf'
        Sha256 = '0AAFB90685CE150D3A86647AB04DC40325C7E9A23A029D2FD4116113591C028C'
    }
)

$expectedReferenceFiles = @(
    'vendor\audiocom\a203\examples\bf01-interconnect\F103_BF01_250401\User\app.c'
    'vendor\audiocom\a203\examples\bf01-interconnect\F103_BootLoader_250401\User\main.c'
    'vendor\audiocom\a203\examples\serial-port-demo\SerialPortDemo\AsyncSockChat\AsyncSockChatDlg.cpp'
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

foreach ($path in $expectedReferenceFiles) {
    $fullPath = Join-Path $repositoryRoot $path
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        Write-Error "Missing extracted reference: $path" -ErrorAction Continue
        $failed = $true
        continue
    }

    Write-Host "OK  $path"
}

if ($failed) {
    exit 1
}

Write-Host 'All reviewed local inputs match.'
