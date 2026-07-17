# Smart Choice

Trợ lý AI so sánh và tư vấn sản phẩm theo nhu cầu thật của khách hàng.
**13 ngành hàng · 2.176 sản phẩm thật của ĐMX · 46 tình huống test tự động.**
Vietnam Innovation Challenge 2026 — đề bài Điện Máy Xanh.

**Demo:** https://demo.aibutler.vn

Nguyên tắc lõi: **LLM chỉ diễn đạt — mọi quyết định là code.** Hỏi ngược có điểm số
giải trình, top 3 kèm trade-off, mọi con số truy được nguồn, chống bịa bằng cơ chế
hậu kiểm chứ không phải lời nhắc.

## Tài liệu

- [Kiến trúc](docs/architecture/kien-truc.md) — luồng xử lý, vì sao thiết kế vậy, số liệu đo
- [Lộ trình pilot 3 tháng](docs/pilot/lo-trinh-pilot.md)
- [Deploy](infra/DEPLOY.md)

## Chạy local — không cần xin dữ liệu gì

```bash
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --port 8000
# -> http://localhost:8000
```

Repo kèm sẵn **catalog mẫu giả lập** (`data/mock/catalog/may_lanh_mau.csv`, sinh lại
bằng `python scripts/sinh_catalog_mau.py`) — clone về là chạy được ngay, đúng yêu cầu
đề bài "dữ liệu demo nên được giả lập hoặc anonymize". Không có `.env` thì hệ chạy
chế độ thuần luật: đủ luồng hỏi ngược + lọc + xếp hạng, chỉ phần diễn đạt là bản mẫu.

Bản demo công khai dùng **dữ liệu thật của ĐMX** (NDA, không nằm trên repo):
đặt file gốc vào `data/raw/` rồi `python scripts/nap_dmx.py` — hệ tự ưu tiên
dữ liệu thật khi có. Khóa API: xem `.env.example`.

## Đo chất lượng

```bash
python scripts/danh_gia.py
# 22 tinh huong khach that: ty le hieu dung o nhu cau, so cau hoi TB, ket cuc, toc do
```
