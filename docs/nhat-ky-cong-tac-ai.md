# Nhật ký cộng tác với AI — SmartChoiceAI

> Bằng chứng cho tiêu chí **"100% AI-native"** của Vietnam Innovation Challenge 2026.
> Toàn bộ sản phẩm được xây dựng qua đối thoại người ↔ AI: AI đề xuất kiến trúc,
> viết mã, săn lỗi, thiết kế UI/UX; người (Wan — chủ sản phẩm, không phải dev)
> định hướng nghiệp vụ và ra quyết định cuối. File này tóm tắt các quyết định
> lớn do AI đề xuất; nhật ký chi tiết là toàn bộ lịch sử hội thoại (hàng trăm lượt).

## 1. AI-native ở đâu trong sản phẩm

Sản phẩm **là** một trợ lý AI hội thoại — không phải app thường gắn thêm nút AI.
Dùng đồng thời **nhiều loại AI**, mỗi loại ở đúng chỗ nó giỏi:

| Loại AI | Model | Việc |
|---|---|---|
| LLM hiểu ngôn ngữ | FPT DeepSeek/Llama · Gemini (đổi 1 dòng env) | Đọc tiếng Việt lộn xộn (viết tắt, không dấu, "20tr", "3x4m") → trích ô nhu cầu |
| LLM diễn đạt | (như trên) | Viết bảng kết quả thành lời tư vấn tự nhiên, đúng giọng sale |
| TTS | FPT.AI-VITs (9 giọng Việt) | Bot đọc câu trả lời — hội thoại 2 chiều bằng giọng |
| STT | Web Speech (→ FPT STT) | Khách nói, hệ nhận |
| Thị giác | Qwen2.5-VL (lộ trình) | Khách chụp nhãn năng lượng/máy cũ → AI đọc |

**Triết lý AI-native có trách nhiệm:** AI làm 2 việc khó nhất mà chỉ AI làm được
(hiểu ngôn ngữ đời thường + diễn đạt tự nhiên). Việc cần *tuyệt đối không sai* —
giá, tồn kho, thông số — thì **code quyết định, và chính AI viết ra bộ luật đó**.
Một trợ lý AI bịa giá là vô dụng; đây là lựa chọn AI-native trưởng thành, không
phải né dùng AI. Bảng "AI đã làm gì trong câu này?" ngay trên giao diện phơi bày
minh bạch từng bước AI vs code cho người dùng (và giám khảo) thấy trực tiếp.

## 2. Các quyết định lớn do AI đề xuất

**Kiến trúc "LLM 2 điểm chạm".** AI phân tích: để LLM tự dẫn hội thoại sẽ *trôi
flow* (hỏi lan man, quên nhu cầu, lật ngược thông tin) và *bịa số*. Đề xuất tách
LLM thành đúng 2 điểm (trích ý + diễn đạt), mọi quyết định là máy trạng thái +
luật. Kết quả: giải trình được, <100ms phần code, chống bịa bằng cơ chế.

**Rổ đơn vị chống hallucination.** AI đề xuất hậu kiểm quét mọi số CÓ ĐƠN VỊ
trong văn LLM, đối chiếu ngược theo *từng rổ* (~30 rổ). Bài học AI tự rút khi
test: "18 hợp lệ ở m² không được bảo lãnh cho '18 dB'" → tách rổ riêng từng đơn vị.

**Đo giá trị thông tin để hỏi ngược thông minh.** AI đề xuất: với mỗi ô trống,
mô phỏng các giá trị → xem top 3 lệch bao nhiêu → chỉ hỏi câu làm *đổi kết quả*.
Nhờ đó phòng 18m² thì hỏi "có nắng không" (điểm 1.00) nhưng bỏ qua câu vô nghĩa.

**Khung ngành generic.** AI nhận ra 11/13 ngành có cùng khuôn xử lý → rút thành
1 khung + mỗi ngành 1 file config JSON. "Thêm ngành = thêm config", không sửa lõi.

**Chống bịa cho cả dữ liệu ngoài luồng.** AI đề xuất: giá KM/quà tặng lấy nguyên
văn từ catalog; ảnh sản phẩm đối chiếu qua cột `productidweb` với CDN chính hãng,
ảnh không xác minh được thì hiện icon — "thà thiếu ảnh chứ không gắn ảnh sai model".

**Sống với dữ liệu bẩn.** AI phân tích 1.039 dòng máy lạnh thật: cột "Công suất
đầu ra" trống 82% → bỏ, thay bằng "Phạm vi sử dụng" (phủ 91%); "Điện năng" là rác
→ thay bằng CSPF từ nhãn năng lượng. Quyết định dựa trên độ phủ thật, không đoán.

## 3. AI tự săn lỗi & tự sửa (trích)

- Quên `if __name__` làm parser chạy mà không ghi file → hệ âm thầm dùng mock;
  AI phát hiện vì top 3 ra tên hãng ẩn danh, thêm guard.
- DeepSeek trả rỗng (nuốt câu trả lời vào phần "suy nghĩ"); AI chẩn đoán qua
  `finish_reason` + `reasoning_content`, thêm cơ chế vớt, và khuyến nghị đổi
  model sang Llama-3.3-Instruct.
- Bộ 23 "câu quái" (XSS, SQL injection, emoji, số âm, phiên giả) do AI tự viết
  để tự kiểm hệ không bao giờ 500 / không bao giờ trả rỗng.

## 4. Bằng chứng kiểm chứng được

- **67 tình huống tự động** (`scripts/danh_gia.py`) — chạy lại 1 lệnh, xanh trên
  cả dữ liệu thật lẫn dữ liệu mẫu công khai.
- **23 câu quái** (`scripts/thu_cau_quai.py`) — không 500, không rỗng.
- **150 test case của BTC** (`scripts/chay_150_tc.py`) — 138 tư vấn, 12 từ chối đúng.
- Mọi con số trên UI bấm được ra nguồn (trường · nguồn · thời điểm · mã SP).

## 5. Vai trò con người

Wan (chủ sản phẩm) đóng vai *định hướng nghiệp vụ*: chọn đề, xác nhận luật thiết
kế (web chốt đơn / chat tư vấn), cung cấp dữ liệu ĐMX, kiểm thử tay và chỉ ra lỗi
thực tế ("nói 0.5 triệu nghe sai", "nút loa tắt không được"). AI đảm nhận toàn bộ
phần kỹ thuật. Đây đúng tinh thần *AI-first*: một người không code vẫn ra được sản
phẩm hoàn chỉnh nhờ cộng tác với AI.
