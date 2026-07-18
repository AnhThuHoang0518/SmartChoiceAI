# SmartChoiceAI — Tài liệu cho AI/dev tiếp quản

> Đọc hết file này trước khi sửa bất cứ dòng nào. Dự án thi Vietnam Innovation
> Challenge 2026, đề Điện Máy Xanh: "Trợ lý AI so sánh và tư vấn sản phẩm theo
> nhu cầu thật". Demo: https://demo.aibutler.vn (landing `/`, chat `/chat`).
> Chủ dự án: Wan (không phải dev — trao đổi bằng ngôn ngữ nghiệp vụ, tiếng Việt,
> sau khi sửa code LUÔN đưa lệnh deploy).

## Nguyên tắc bất khả xâm phạm

1. **LLM chỉ chạm đúng 2 điểm mỗi lượt**: (a) trích ô nhu cầu → JSON, (b) diễn
   đạt bảng kết quả đã tính. Mọi quyết định — hỏi gì, lọc gì, xếp ai trên,
   so sánh, khuyến mãi, giải trình — là CODE. Đề xuất "cho LLM tự dẫn hội
   thoại / kiến trúc agent tự do" đã bị bác có chủ đích (dự án trước của Wan
   từng trôi flow phải đập đi). KHÔNG viết lại phần này bằng LLM-driven agent.
2. **Không bịa**: giá/thông số/tồn kho/quà chỉ từ catalog. Hậu kiểm
   (`backend/app/guardrails/hau_kiem.py`) quét mọi số CÓ ĐƠN VỊ trong văn LLM,
   đối chiếu ngược theo TỪNG RỔ đơn vị (~30 rổ; 18 hợp lệ ở m² không bảo lãnh
   "18 dB"). Rổ `phan_tram` cố ý chỉ nhận % có thật trong dữ liệu.
   Chặn → bắt viết lại 1 lần (quá 6s thì thôi) → bản dự phòng template.
3. **Thiếu thì nói, không đoán** (5 tầng): thiếu giá/trường sống còn → loại
   khỏi catalog; thiếu số đối chiếu ràng buộc → BỎ + ĐẾM + khai "bỏ N máy
   thiếu dữ liệu"; thiếu số chấm điểm → 0.5 trung tính; trường suy luận → cờ
   `suy_luan` + cảnh báo UI; cả ngành không có sheet (tivi/laptop/điện thoại)
   → từ chối thẳng. Ảnh cũng vậy: không xác minh được thì hiện icon, không độ.
4. **Không tự chế ngưỡng nghiệp vụ**: "tầm trung" = tercile giá THẬT của ngành;
   map mục-đích→ngưỡng (tablet học online mấy inch...) đang TRỐNG chờ người
   hiểu bán hàng chốt — cấm AI tự điền.
5. **Không đoán API**: mọi endpoint FPT (LLM `/chat/completions`, TTS
   `/audio/speech`) đều lấy từ tài liệu chính thức (github.com/fpt-corp/
   ai-marketplace + trang model). Pattern ảnh CDN đã kiểm chứng thực nghiệm.
6. **NDA**: `data/raw/Spec_cate_gia.xlsx`, `data/processed/*` (CSV giá thật +
   `anh_sp.json`), `.env`, `evaluations/datasets/testcase_viac_150.xlsx`,
   `evaluations/results/ket_qua_150_tc.xlsx` — KHÔNG BAO GIỜ lên git.
   Đã có 2 lớp chặn: `.gitignore` + `deploy.ps1` (pattern nhạy cảm → dừng đỏ).
   Lịch sử repo đã được filter-repo làm sạch 19/07 — **đừng push từ clone cũ
   trước thời điểm đó** (lịch sử cũ sẽ quay lại). Dữ liệu lên VPS bằng scp tay.

## Kiến trúc 1 lượt chat

```
tin nhắn → chuẩn hóa TV (viết tắt/không dấu/20tr/triệu rưỡi/3x4m/đếm người)
  → intent phụ (code): so sánh 2 máy · vì sao chọn · hãng nào · khuyến mãi
    · tồn kho(từ chối) · chủ quan(từ chối) · giải thích công suất · ngoài phạm vi
  → router ngành (máy lạnh | tủ lạnh | 11 ngành khung | chào hỏi ngành)
  → trích ô nhu cầu (regex config + LLM vớt phần thiếu) + hãng + inverter + tầm giá
  → thiếu ô bắt buộc? → đo GIÁ TRỊ THÔNG TIN → 1 câu hỏi template + chip gợi ý
  → đủ → lọc cứng → chấm điểm (trọng số từ lời khách) → top 3 + trade-off
  → LLM viết lại (max 150 từ) → hậu kiểm → text + card (ảnh, quà, badge nguồn)
```

## Bản đồ file

| File | Vai trò |
|---|---|
| `backend/app/api/chat.py` | Router + mọi intent phụ + TTS `/api/doc` + `/api/khuyen-mai` + `/api/nhan-truong` |
| `backend/app/core/chuan_hoa_tv.py` | Chuẩn hóa TV + toàn bộ detector (so sánh, hãng, mức giá, đếm người...) |
| `backend/app/agents/` | `trich_o_nhu_cau` (LLM #1 + luật), `viet_lai` (LLM #2 + vòng hậu kiểm), `gia_tri_thong_tin` |
| `backend/app/guardrails/hau_kiem.py` | Rổ đơn vị chống bịa |
| `backend/app/ranking/xep_hang.py` | Vertical MÁY LẠNH: lọc/chấm/trade-off |
| `backend/app/nganh/tu_lanh.py` | Vertical TỦ LẠNH riêng (chạy trước khi có khung — hợp nhất SAU hackathon) |
| `backend/app/nganh/khung.py` | KHUNG GENERIC 11 ngành: thêm ngành = thêm `configs/nganh/*.json` + 1 mục parser |
| `backend/app/core/nhan_truong.py` | Nhãn TV cho trường + `tien_chu` (15,5 triệu — PHẨY, TTS đọc "phẩy") |
| `backend/app/services/llm.py` | Adapter FPT/Gemini/luật; DeepSeek hay trả rỗng → có vớt reasoning; đổi model qua `.env` `LLM_MODEL` |
| `configs/may_lanh.json`, `configs/nganh/*.json` | TOÀN BỘ tri thức ngành: ô, regex, luật lọc, trục chấm, template |
| `frontend/chat/index.html` | Trang chat 1 file: dark mode, mic, TTS+mặt nhép miệng, panel ảnh, chip |
| `frontend/src/` + `frontend/dist/` | Landing React (Vite). SỬA src xong PHẢI build lại, dist ĐƯỢC commit (VPS không có node) |
| `scripts/nap_dmx*.py` | Parser 14 sheet → `data/processed/*.csv` (chạy lại khi đổi cột) |
| `scripts/danh_gia.py` | 74 tình huống — PHẢI XANH trước mọi lần deploy |
| `scripts/thu_cau_quai.py` | 23 câu ác ý: không 500, không rỗng |
| `scripts/chay_150_tc.py` | Chạy bộ test BTC (mỗi case 1 phiên!) |
| `scripts/lay_anh_dmx.py` | Ảnh chính chủ theo `productidweb` (chạy máy Wan) |
| `scripts/do_llm_that.py`, `scripts/kiem_llm.py` | Đo LLM thật / soi lỗi LLM |

## Deploy & hạ tầng

- Một lệnh (chạy TRONG `E:\huhu\exe7\SmartChoiceAI`): `.\deploy.ps1 "mo ta"`
  = chặn file nhạy cảm → commit → push → VPS pull → restart → healthz.
- VPS: `root@45.117.170.223`, code `/opt/smartchoice`, service `smartchoice`
  (port 8100, Caddy proxy demo.aibutler.vn). Dữ liệu processed + `.env` KHÔNG
  theo git — đổi thì scp tay + `systemctl restart smartchoice`.
- `.env` (cả máy Wan lẫn VPS): `LLM_NHA_CUNG_CAP=fpt`, `LLM_API_KEY=...`,
  `LLM_MODEL=Llama-3.3-70B-Instruct` (DeepSeek-V4-Flash là model suy luận,
  hay nuốt câu trả lời vào phần nghĩ — tránh), `TTS_GIONG=std_kimngan`.
- CI GitHub Actions (`.github/workflows/ci.yml`) chạy pytest + `danh_gia.py` +
  `thu_cau_quai.py` mỗi push/PR (cả 3 đều chạy `LLM_NHA_CUNG_CAP=luat`, không
  cần mạng/API key).

## Kiểm tra bắt buộc sau MỌI thay đổi

```bash
python scripts/danh_gia.py        # 74/74 (mock: tự bỏ các case cần data thật)
python scripts/thu_cau_quai.py    # không 500, không rỗng
```
Bài học lặp 4 lần: kỳ vọng test phụ thuộc dữ liệu → catalog mẫu (hãng ẩn danh
Alpha/Bravo) có thể ra kết cục khác data thật; case như vậy đánh dấu
`can_du_lieu_that: true` hoặc nới `ky_vong_loai: bat_ky_khong_loi`.

## Trạng thái (19/07/2026) & việc mở

- Xong: 14 ngành (2 sheet micro gộp, phân biệt qua cột `nhom`) · 2.176 SKU ·
  74 tình huống + 23 câu quái + 150 TC hỗ trợ · so sánh trực tiếp · giải trình
  xếp hạng · hãng/inverter/tầm giá/quà/bình lít/SIM/ATM/ELCB/CPU/loa/phủ màu/
  ngăn đá/trang-tháng · giọng 2 chiều (mic + TTS VITs, mặt nhép miệng) ·
  ảnh chính chủ theo productidweb · UI tông ĐMX xanh+vàng.
- Mở: (1) chạy `lay_anh_dmx.py` hết 2.176 SKU rồi scp (đã xong ~90 máy lạnh);
  (2) 4 ngưỡng mục-đích chờ Wan; (3) hợp nhất 2 vertical vào khung — SAU thi;
  (4) video theo `docs/video-script.md` + slide + nộp.
- Nhánh: main = bản live. Làm gì cũng ở nhánh riêng, PR vào main, KHÔNG force
  push, KHÔNG để công cụ sinh code (Codex...) đè main trước giờ chấm.

## Điều cấm nhanh (cho AI sinh code)

- Không refactor lan man / đổi kiến trúc sang LLM-driven.
- Không thêm số liệu, ngưỡng, đánh giá sao, tồn kho — không có trong dữ liệu.
- Không commit file trong `data/`, `.env`, file BTC; không xóa `.gitignore` rule.
- Không sửa `frontend/src` mà quên build dist; không sửa CSV processed tay
  (sửa parser rồi chạy lại).
- Xưng hô trong MỌI text khách thấy: bot xưng "em", gọi "anh chị" (không gạch
  chéo), tiền viết "15,5 triệu"/"500 nghìn".
