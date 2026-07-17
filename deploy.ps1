# Deploy Smart Choice - mot lenh: commit -> push -> VPS pull -> restart -> kiem
#
#   .\deploy.ps1 "mo ta thay doi"
#
# Giong het deploy.ps1 cua AI Butler. Luu y:
# - KHONG dong toi 2 file mat (.env, data/) - chung da gitignore, chi scp tay khi doi.
# - Kiem /healthz sau khi restart; loi thi in log service ra luon.

param([string]$m = "cap nhat")

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# Chan push nham file mat (phong khi ai do sua .gitignore)
$nhay_cam = git status --porcelain | Select-String -Pattern "Spec_cate_gia|\.env$|may_lanh\.csv"
if ($nhay_cam) {
    Write-Host "DUNG LAI: file nhay cam sap bi commit:" -ForegroundColor Red
    $nhay_cam
    exit 1
}

git add -A
git commit -m $m
if ($LASTEXITCODE -ne 0) { Write-Host "Khong co gi de commit - van cap nhat VPS..." }
git push

Write-Host "`n--- VPS: pull + restart ---"
ssh root@45.117.170.223 "cd /opt/smartchoice && git pull && systemctl restart smartchoice && sleep 2 && curl -s localhost:8100/healthz || journalctl -u smartchoice -n 20 --no-pager"

Write-Host "`nXong. Kiem: https://demo.aibutler.vn"
