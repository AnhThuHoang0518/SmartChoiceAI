# Kịch bản video demo 3 phút

> Quay màn hình https://demo.aibutler.vn + lồng tiếng. Mỗi cảnh ghi sẵn lời thoại — đọc chậm là vừa khung giờ.

## Cảnh 1 — Vấn đề (0:00–0:25)

Chiếu trang so sánh thông số kiểu cũ (bảng đầy RAM/BTU/dB).

> "Khách mua máy lạnh không cần bảng thông số — họ cần biết máy nào hợp với PHÒNG CỦA HỌ. Smart Choice hỏi đúng vài câu quyết định, rồi tư vấn bằng ngôn ngữ người thường, trên dữ liệu thật của Điện Máy Xanh — 269 máy lạnh đang bán."

## Cảnh 2 — Kịch bản chuẩn của đề bài (0:25–1:15)

Gõ đúng câu trong đề: `e muon mua may lanh duoi 20tr cho phong 18m2, tk dien, it on`

> "Viết tắt, không dấu — hệ thống vẫn hiểu: ngân sách 20 triệu, phòng 18m², ưu tiên tiết kiệm điện và ít ồn. Nó KHÔNG hỏi cả đống — nó chỉ hỏi câu làm thay đổi kết quả."

Chỉ vào dòng "Vì sao hỏi câu này: co_nang = 1.00".

> "Đây là điểm khác biệt: mỗi câu hỏi có điểm số. Nắng chiều làm thay đổi toàn bộ danh sách máy phù hợp — nên nó hỏi. Còn phòng ngủ hay phòng khách? Với ca này không đổi kết quả — nên nó không làm phiền khách."

Trả lời `co, chieu nang lam` → hiện top 3.

> "Top 3, mỗi máy nói rõ ĐƯỢC gì và MẤT gì — không có máy nào 'tốt toàn diện'. Và dòng này: 'Vì sao em không đề xuất' — chính là máy khách hay thấy quảng cáo giá tốt, nhưng thiếu tải cho phòng có nắng. Tư vấn thật là phải dám nói câu đó."

## Cảnh 3 — Chống bịa sống (1:15–1:50)

Bấm badge ⓘ cạnh giá.

> "Mọi con số truy được về nguồn: field nào, API nào, lấy lúc nào, mã sản phẩm nào. AI không được phép có số 'tự nhiên mà có'."

Chỉ dòng thống kê "đã chặn bịa: N lần" (nếu có trong phiên quay — nếu không, chiếu ảnh chụp phiên trước).

> "Và đây là lúc chốt chặn làm việc thật: model vừa định nói một con số không có trong dữ liệu — bị chặn, bắt viết lại. Chống hallucination ở đây là cơ chế chạy từng câu trả lời, không phải lời hứa trong slide."

## Cảnh 4 — Giọng nói + đổi ý (1:50–2:25)

Bấm 🎤, nói: "nếu giảm còn mười lăm triệu thì sao"

> "Nói chuyện bằng giọng — và để ý: khách vừa ĐỔI ngân sách giữa chừng. Hệ thống ghi đè đúng ô đó, giữ nguyên mọi thứ đã biết, tính lại từ đầu. Không trôi ngữ cảnh."

Gõ thử `có tủ lạnh nào xịn không`:

> "Hỏi ngoài phạm vi thì nói thẳng — và đây không phải lời xin lỗi suông: dữ liệu 14 ngành hàng đã nạp sẵn, thêm ngành mới chỉ là thêm một file cấu hình."

## Cảnh 5 — Số liệu + kiến trúc (2:25–3:00)

Chiếu bảng: 22/22 tình huống · 100% ô nhu cầu đúng · 1,0 câu hỏi trung bình · 0 hallucination lọt · xử lý ngoài LLM <35ms. Rồi sơ đồ kiến trúc.

> "Toàn bộ đo được, chạy lại được bằng một lệnh. Kiến trúc: LLM chỉ xuất hiện đúng hai chỗ — hiểu lời khách và diễn đạt kết quả. Mọi quyết định là code: lặp lại được, giải trình được, và chạy trên hạ tầng model tại Việt Nam qua FPT AI Marketplace — đổi nhà cung cấp bằng một dòng cấu hình. Smart Choice — tư vấn như người bán hàng giỏi nhất của bạn, nhưng không bao giờ bịa."

## Ghi chú quay

- Quay 1 lần liền mạch nếu được — giám khảo tin bản không cắt ghép.
- Zoom chữ to (Ctrl +) trước khi quay.
- Chuẩn bị sẵn phiên dự phòng đã chạy tốt trong tab khác, phòng mạng chậm lúc quay.
- Nếu câu trả lời LLM lượt quay bị chậm >5s, cắt cảnh chờ, giữ timestamp thống kê ms trên màn hình.
