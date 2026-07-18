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

# Chan push nham file mat (phong khi ai do sua .gitignore). Chi canh thu THAT
# nhay cam: file goc DMX, .env, csv gia that trong data/processed, file BTC.
$nhay_cam = git status --porcelain | Select-String -Pattern "Spec_cate_gia|\.env$|data/processed/.*\.csv|testcase_viac|ket_qua_150"
if ($nhay_cam) {
    Write-Host "DUNG LAI: file nhay cam sap bi commit:" -ForegroundColor Red
    $nhay_cam
    exit 1
}

git add -A
git commit -m $m
if ($LASTEXITCODE -ne 0) { Write-Host "Khong co gi de commit - van cap nhat VPS..." }

# Push fail (mat mang, DNS...) ma van chay tiep thi VPS pull ra ban CU
# va script bao "Xong" lao -> dung ngay tai day. (Bai hoc tu lan deploy dau:
# 'Could not resolve host' nhung van in Xong.)
git push
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nPUSH THAT BAI - thuong do mang/DNS. Commit van nam local, khong mat gi." -ForegroundColor Red
    Write-Host "Thu lai:  git push   (roi chay lai .\deploy.ps1 hoac tu ssh pull)" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n--- VPS: pull + restart ---"
ssh root@45.117.170.223 "cd /opt/smartchoice && git pull && systemctl restart smartchoice && sleep 2 && curl -s localhost:8100/healthz || journalctl -u smartchoice -n 20 --no-pager"

Write-Host "`nXong. Kiem: https://demo.aibutler.vn"
