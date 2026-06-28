<#
  Capture the ats-mini display over USB serial and save it as PNG.

  Requires the radio setting  Settings -> USB Port -> Ad hoc  (enables the
  serial command protocol; the 'C' command dumps the screen as a BMP in HEX).

  Usage:
    powershell -File tools/capture-screenshot.ps1 -Port COM7 -OutDir .
  The COM port differs per PC: find the ESP32-S3 (VID_303A / PID_1001) with
    Get-CimInstance Win32_PnPEntity | ? {$_.Name -match 'COM\d+'}
#>
param(
  [string]$Port   = "COM7",
  [string]$OutDir = "."
)
$ErrorActionPreference = "Stop"
$hex = Join-Path $OutDir "screenshot.hex"
$png = Join-Path $OutDir "screenshot.png"

$sp = New-Object System.IO.Ports.SerialPort($Port,115200,'None',8,'One')
$sp.DtrEnable = $false; $sp.RtsEnable = $false   # do NOT reset the device
$sp.ReadTimeout = 500
$sp.Open()
Start-Sleep -Milliseconds 300
$sp.DiscardInBuffer()
$sp.Write("C")                                    # request screenshot

$sb = New-Object System.Text.StringBuilder
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$last = 0
while ($sw.ElapsedMilliseconds -lt 15000) {
  $c = $sp.ReadExisting()
  if ($c.Length) { [void]$sb.Append($c); $last = $sw.ElapsedMilliseconds }
  elseif (($sw.ElapsedMilliseconds - $last) -gt 1200 -and $last -gt 0) { break }
  Start-Sleep -Milliseconds 40
}
$sp.Close()

[System.IO.File]::WriteAllText($hex, $sb.ToString())
Write-Host "captured $($sb.Length) chars -> $hex"
python (Join-Path $PSScriptRoot "hex2png.py") $hex $png
Write-Host "image -> $png"
