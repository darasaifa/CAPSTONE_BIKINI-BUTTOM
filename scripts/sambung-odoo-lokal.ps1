# Menyambungkan folder addons repo ini ke Odoo 19 yang terpasang di Windows.
#
# Jalankan di PowerShell sebagai ADMINISTRATOR, dari folder repo:
#   powershell -ExecutionPolicy Bypass -File .\scripts\sambung-odoo-lokal.ps1
#
# Hanya me-restart layanan Odoo (misalnya setelah git pull yang mengubah file .py):
#   powershell -ExecutionPolicy Bypass -File .\scripts\sambung-odoo-lokal.ps1 -RestartSaja
#
# Yang diubah di odoo.conf (salinan cadangan dibuat dulu):
#   - addons_path   = addons bawaan Odoo + folder addons repo ini
#   - http_interface = 127.0.0.1 (Odoo hanya bisa dibuka dari laptop sendiri)
# Kata sandi di odoo.conf tidak dibaca, tidak ditampilkan, dan tidak diubah.

param([switch]$RestartSaja)
$ErrorActionPreference = 'Stop'
$layanan = 'odoo-server-19.0'

$admin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $admin) {
    Write-Host 'Jalankan PowerShell sebagai administrator (klik kanan > Run as administrator), lalu ulangi.' -ForegroundColor Red
    exit 1
}

if (-not (Get-Service $layanan -ErrorAction SilentlyContinue)) {
    Write-Host "Layanan $layanan tidak ditemukan. Pastikan yang terpasang Odoo 19 (bukan 20)." -ForegroundColor Red
    exit 1
}

if (-not $RestartSaja) {
    $kunci = @(
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Odoo 19.0',
        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Odoo 19.0'
    )
    $folderOdoo = $null
    foreach ($k in $kunci) {
        $p = Get-ItemProperty $k -ErrorAction SilentlyContinue
        if ($p -and $p.InstallLocation) { $folderOdoo = $p.InstallLocation.Trim('"'); break }
    }
    if (-not $folderOdoo) { Write-Host 'Folder instalasi Odoo 19 tidak ditemukan.' -ForegroundColor Red; exit 1 }

    $conf = Join-Path $folderOdoo 'server\odoo.conf'
    $addonsBawaan = Join-Path $folderOdoo 'server\odoo\addons'
    $addonsRepo = (Resolve-Path (Join-Path $PSScriptRoot '..\addons')).Path
    if (-not (Test-Path $conf)) { Write-Host "Tidak ada $conf" -ForegroundColor Red; exit 1 }

    $cadangan = "$conf.bak-$(Get-Date -Format yyyyMMdd-HHmmss)"
    Copy-Item $conf $cadangan

    $isi = [IO.File]::ReadAllText($conf)
    $isi = $isi -replace '(?m)^addons_path[ \t]*=[^\r\n]*', "addons_path = $addonsBawaan,$addonsRepo"
    if ($isi -match '(?m)^http_interface[ \t]*=') {
        $isi = $isi -replace '(?m)^http_interface[ \t]*=[^\r\n]*', 'http_interface = 127.0.0.1'
    } else {
        $isi = $isi -replace '(?m)^\[options\][^\r\n]*', "`$0`r`nhttp_interface = 127.0.0.1"
    }
    [IO.File]::WriteAllText($conf, $isi, (New-Object Text.UTF8Encoding($false)))

    Write-Host "odoo.conf diperbarui (cadangan: $cadangan)"
    Write-Host "  addons_path    = $addonsBawaan,$addonsRepo"
    Write-Host '  http_interface = 127.0.0.1'
}

Write-Host "Me-restart layanan $layanan ..."
Restart-Service $layanan
Start-Sleep -Seconds 5
(Get-Service $layanan).Status
Write-Host 'Selesai. Buka http://localhost:8069' -ForegroundColor Green
