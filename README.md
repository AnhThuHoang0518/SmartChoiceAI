# Smart Choice

Trợ lý AI so sánh và tư vấn sản phẩm theo nhu cầu thật của khách hàng.
Vietnam Innovation Challenge 2026 — đề bài Điện Máy Xanh.

**Demo:** https://demo.aibutler.vn

Nguyên tắc lõi: **LLM chỉ diễn đạt — mọi quyết định là code.** Hỏi ngược có điểm số
giải trình, top 3 kèm trade-off, mọi con số truy được nguồn, chống bịa bằng cơ chế
hậu kiểm chứ không phải lời nhắc.

## Tài liệu

- [Kiến trúc](docs/architecture/kien-truc.md) — luồng xử lý, vì sao thiết kế vậy, số liệu đo
- [Lộ trình pilot 3 tháng](docs/pilot/lo-trinh-pilot.md)
- [Deploy](infra/DEPLOY.md)

## Chạy local

```bash
pip install -r requirements.txt
# Can 2 file khong co tren repo (du lieu doi tac + khoa API):
#   data/processed/may_lanh.csv  (sinh tu: python scripts/nap_dmx.py voi file goc trong data/raw/)
#   .env                         (xem .env.example)
python -m uvicorn backend.app.main:app --port 8000
# -> http://localhost:8000
```

## Đo chất lượng

```bash
python scripts/danh_gia.py
# 22 tinh huong khach that: ty le hieu dung o nhu cau, so cau hoi TB, ket cuc, toc do
```
