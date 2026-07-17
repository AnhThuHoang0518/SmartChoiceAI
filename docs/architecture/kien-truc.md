# Kiến trúc Smart Choice

> Trợ lý AI tư vấn điện máy theo nhu cầu thật — Vietnam Innovation Challenge 2026, đề bài Điện Máy Xanh.
> Demo: https://demo.aibutler.vn · Nguyên tắc lõi: **LLM chỉ diễn đạt, mọi quyết định là code.**

## Luồng một lượt chat

```
Khách nhắn (text / 🎤 giọng nói)
  → Chuẩn hóa tiếng Việt        [code]  không dấu, viết tắt, 20tr/1 tỷ/9990k, m², lỗi chính tả
  → Trích ô nhu cầu             [LLM #1] chỉ điền JSON đúng khuôn; luật regex chạy trước, LLM chỉ vớt phần thiếu
  → Máy trạng thái phía server  [code]  ô đã biết không bị ghi đè — trừ khi khách CHỦ ĐỘNG đổi ý
  → Đủ ô chưa?
      CHƯA → Đo giá trị thông tin [code]  mô phỏng từng ô trống: điền vào thì top 3 đổi bao nhiêu?
            → 1 câu hỏi template  [code]  KHÔNG qua LLM → không lan man, không bịa
      RỒI  → Lọc cứng             [code]  phạm vi m² hãng công bố (nắng → tải nhiệt ×1,3), ngân sách
           → Chấm điểm            [code]  trọng số sinh từ chính lời khách; CSPF, độ ồn, giá, Turbo
           → Top 3 + trade-off    [code]  hơn gì / kém gì / vì sao loại máy khách đang nhắm
           → Viết lại             [LLM #2] chỉ nhìn thấy bảng kết quả — không có quyền tra catalog
           → Hậu kiểm số          [code]  quét mọi số theo ĐƠN VỊ, đối chiếu ngược; lệch → chặn, viết lại
           → Trả khách            mỗi con số kèm badge nguồn (field · nguồn · thời điểm · mã SP)
```

**Đúng 2 lần chạm LLM mỗi lượt.** Mọi bước quyết định (hỏi gì, lọc gì, xếp ai trên) đều là code — lặp lại được, giải trình được, 0ms.

## Vì sao thiết kế như vậy

**Flow do code điều khiển, không phải LLM.** Để LLM tự dẫn hội thoại là trôi flow: hỏi lan man, quên nhu cầu ban đầu, lượt sau lật ngược lượt trước. Máy trạng thái server + câu hỏi template cứng loại bỏ cả lớp lỗi này bằng cấu trúc, không phải bằng lời nhắc trong prompt.

**Hỏi ngược đo được, không đoán.** Với mỗi ô còn trống, hệ mô phỏng: nếu ô này nhận các giá trị khác nhau, top 3 lệch bao nhiêu (khác tập 0,5 + khác thứ tự 0,2 + đổi hạng nhất 0,3)? Vượt ngưỡng 0,25 mới hỏi. Kết quả thực tế: phòng 18m² thì "có nắng không" được 1,00 (hỏi ngay — vì nắng đẩy sang dải máy khác), nhưng phòng 22m² thì nắng chỉ 0,00 (không hỏi — dải 20-30m² phủ cả hai). **Thuật toán tự biết lúc nào một câu hỏi là vô nghĩa.** API trả kèm bảng điểm này để giải trình từng câu hỏi.

**Chống bịa là cơ chế, không phải lời khuyên.** Bốn tầng: (1) LLM viết-lại chỉ được cấp bảng kết quả đã tính, không có quyền truy vấn; (2) hậu kiểm trích mọi con số có đơn vị trong bản nháp, đối chiếu ngược theo từng rổ đơn vị — 18 hợp lệ ở rổ m² không bảo lãnh cho "18 dB"; (3) chặn thì báo lỗi cụ thể và bắt viết lại 1 lần, quá là về bản dự phòng template (khô nhưng mọi số đều thật); (4) mỗi khẳng định gắn nguồn truy được trên UI. Đã bắt bịa thật trên production ("đã chặn bịa: 1 lần" hiển thị ngay trên demo).

**Sống được với dữ liệu bẩn.** Đo trên 1.039 dòng máy lạnh thật của ĐMX: cột "Công suất đầu ra" trống 82% → bỏ, thay bằng "Phạm vi sử dụng" hãng công bố (91%); "Điện năng tiêu thụ" là rác ('0','1','2') → thay bằng CSPF từ nhãn năng lượng (đọc được 100%); độ ồn 452 định dạng → parser lấy min dàn lạnh (98%). Trường phải suy luận từ mô tả gắn cờ `suy_luan` — chỉ được gợi ý, cấm khẳng định.

**Không khóa nhà cung cấp model.** Adapter đổi LLM bằng 1 dòng env: FPT AI Marketplace (DeepSeek-V4-Flash — hạ tầng Việt Nam, API đọc từ tài liệu chính thức github.com/fpt-corp/ai-marketplace) ↔ Gemini ↔ chế độ thuần luật (mất LLM vẫn chạy đủ luồng hỏi-lọc-xếp hạng, chỉ kém phần diễn đạt — CI chạy không cần khóa API).

## Số liệu đo được (bộ 22 tình huống, chạy lại bằng `python scripts/danh_gia.py`)

| Chỉ số | Kết quả |
|---|---|
| Tình huống đạt | 22/22 |
| Ô nhu cầu trích đúng | 100% (34/34) |
| Số câu hỏi trung bình để ra tư vấn | 1,0 |
| Xử lý ngoài LLM | <35ms |
| Hallucination lọt qua hậu kiểm | 0 |

Bộ tình huống phủ: không dấu, viết tắt, 20tr/1 tỷ/9990k, số thập phân, trả lời cụt "khong", trả lời lạc đề, đổi ý giữa chừng ("nếu giảm còn 10 triệu?" → ghi đè thật), ngoài phạm vi (tủ lạnh/máy giặt → nói thẳng), ngân sách quá thấp (0 máy → báo giá thấp nhất đủ tải).

## Nhân rộng 14 ngành hàng

Toàn bộ tri thức ngành nằm trong `configs/may_lanh.json` (ô nhu cầu, hệ số tải nhiệt, trọng số, ngưỡng hỏi, template) — code không chứa gì riêng của máy lạnh. Dữ liệu ĐMX có sẵn 14 sheet (tủ lạnh 1.693 SKU, máy giặt 1.338, máy tính bảng 1.470...). **Thêm ngành = thêm 1 file config + 1 parser sheet**, không sửa lõi.

## Ánh xạ với flow thiết kế 14 bước

| Bước thiết kế | Trạng thái |
|---|---|
| 1-3 Conversation State, hiểu nhu cầu, hỏi bổ sung | ✅ chạy (kèm đo giá trị thông tin — vượt thiết kế) |
| 4-5 Planner + Ontology | ✅ dạng config + code (chủ ý: lặp lại được, 0ms) |
| 6a Structured Retrieval | ✅ chạy |
| 6b-7 Document Retrieval + Rerank | 🔜 pilot (chờ dữ liệu Policy&FAQ của BTC; dùng e5-large + bge-reranker trên FPT) |
| 8-10 Hard Filter, Scoring, Ranking | ✅ chạy |
| 11-12 Evidence + Grounded Generation | ✅ chạy (bảng kết quả + nguồn từng trường) |
| 13 Schema/Numeric Validator | ✅ chạy · Claim-Source/Groundedness định tính: 🔜 pilot |
| 14 Safe Fallback | ✅ chạy (bản dự phòng + "chưa có dữ liệu") |
