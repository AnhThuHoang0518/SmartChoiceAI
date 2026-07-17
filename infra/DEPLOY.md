# Deploy demo lên VPS (demo.aibutler.vn)

> VPS dùng chung với AI Butler đang chạy thật → Smart Choice ở port **8100**,
> thư mục **/opt/smartchoice**, service **smartchoice** — không đụng gì của aibutler.

## 0. DNS (làm TRƯỚC, certbot cần nó)

Vào trang quản lý DNS của `aibutler.vn`, thêm bản ghi:

| Loại | Tên | Trỏ tới |
|---|---|---|
| A | demo | 45.117.170.223 |

## 1. Trên VPS — cài app

```bash
ssh root@45.117.170.223
git clone https://github.com/AnhThuHoang0518/SmartChoiceAI.git /opt/smartchoice
cd /opt/smartchoice
python3 -m venv venv
venv/bin/pip install -r requirements.txt
exit
```

## 2. Từ máy Windows — chép 2 file KHÔNG có trên GitHub (cố ý gitignore)

```powershell
scp E:\huhu\exe7\SmartChoiceAI\data\processed\may_lanh.csv root@45.117.170.223:/opt/smartchoice/data/processed/
scp E:\huhu\exe7\SmartChoiceAI\.env root@45.117.170.223:/opt/smartchoice/.env
```

- `may_lanh.csv`: dữ liệu ĐMX (NDA) — không bao giờ nằm trên repo public.
- `.env`: khóa API — như trên.

## 3. Trên VPS — bật service + HTTPS

```bash
ssh root@45.117.170.223
cd /opt/smartchoice
cp infra/smartchoice.service /etc/systemd/system/
systemctl daemon-reload && systemctl enable --now smartchoice
curl -s localhost:8100/healthz        # phải ra {"ok":true}

cp infra/nginx-demo.conf /etc/nginx/sites-available/demo.aibutler.vn
ln -s /etc/nginx/sites-available/demo.aibutler.vn /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
certbot --nginx -d demo.aibutler.vn   # tự cấp SSL + sửa config
```

## 4. Kiểm

- https://demo.aibutler.vn → giao diện chat
- Chat thử: `e muon mua may lanh duoi 20tr cho phong 18m2, tk dien, it on`
- Nút 🎤 chỉ chạy sau khi có HTTPS (bước certbot)

## Cập nhật code sau này

```bash
ssh root@45.117.170.223 "cd /opt/smartchoice && git pull && systemctl restart smartchoice"
```

## Gỡ toàn bộ (sau hackathon, nếu muốn)

```bash
systemctl disable --now smartchoice
rm /etc/systemd/system/smartchoice.service /etc/nginx/sites-enabled/demo.aibutler.vn /etc/nginx/sites-available/demo.aibutler.vn
systemctl reload nginx && rm -rf /opt/smartchoice
```
