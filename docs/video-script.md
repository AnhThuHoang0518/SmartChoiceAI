# Kịch bản video demo 3 phút

> Quay màn hình https://demo.aibutler.vn + lồng tiếng. Mỗi cảnh ghi sẵn lời thoại — đọc chậm là vừa khung giờ.

## Cảnh 1 — Vấn đề (0:00–0:20)

Chiếu trang so sánh thông số kiểu cũ (bảng đầy RAM/BTU/dB).

> "Khách mua điện máy không cần bảng thông số — họ cần biết máy nào hợp với nhu cầu THẬT của họ. Smart Choice hỏi đúng vài câu quyết định rồi tư vấn bằng ngôn ngữ người thường, trên dữ liệu thật của Điện Máy Xanh: 13 ngành hàng, 2.176 sản phẩm đang bán."

## Cảnh 2 — Kịch bản chuẩn của đề bài (0:20–1:05)

Gõ đúng câu trong đề: `e muon mua may lanh duoi 20tr cho phong 18m2, tk dien, it on`

> "Viết tắt, không dấu — hệ thống vẫn hiểu: ngân sách 20 triệu, phòng 18m², ưu tiên tiết kiệm điện và ít ồn. Nó KHÔNG hỏi cả đống — chỉ hỏi câu làm thay đổi kết quả."

Chỉ vào dòng "Vì sao hỏi câu này: co_nang = 1.00".

> "Mỗi câu hỏi có điểm số. Nắng chiều làm đổi toàn bộ danh sách máy phù hợp — nên nó hỏi. Phòng ngủ hay phòng khách với ca này không đổi kết quả — nên nó không làm phiền."

Trả lời `co, chieu nang lam` → hiện top 3.

> "Top 3, mỗi máy nói rõ ĐƯỢC gì — MẤT gì: rẻ hơn, êm hơn, chịu thiệt chỗ nào. Máy đang khuyến mãi hiện giá gốc gạch và mức giảm THẬT. Và dòng 'Vì sao em không đề xuất' — máy quảng cáo giá tốt nhưng thiếu tải cho phòng có nắng. Tư vấn thật là dám nói câu đó."

## Cảnh 3 — So sánh trực tiếp + chống bịa (1:05–1:45)

Bấm nút **⚖ So sánh với máy 1** trên card máy 2.

> "Đề bài tên là 'so sánh sản phẩm' — đây: bảng đối chiếu từng thông số, kết luận rẻ hơn bao nhiêu tiền. Bảng này do CODE dựng từ dữ liệu có nguồn, không qua model sinh chữ — nên không thể bịa và trả về tức thì."

Bấm badge ⓘ cạnh Giá.

> "Mọi con số truy được về nguồn: trường nào, API nào, lấy lúc nào, mã sản phẩm nào. Còn khi model định nói một số KHÔNG có trong dữ liệu — dòng 'đã chặn bịa' này — nó bị chặn và bắt viết lại. Chống hallucination là cơ chế chạy từng câu, không phải lời hứa trong slide."

## Cảnh 4 — Giọng nói, đổi ý, đổi ngành (1:45–2:25)

Bấm 🎤, nói: "nếu giảm còn mười lăm triệu thì sao"

> "Nói bằng giọng — và khách vừa ĐỔI ngân sách giữa chừng: hệ thống ghi đè đúng ô đó, giữ mọi thứ đã biết, tính lại từ đầu."

Gõ `thế còn tủ lạnh thì sao`:

> "Đổi hẳn ngành giữa cuộc nói chuyện — nó chuyển sang tủ lạnh và MANG ngân sách 15 triệu theo, không bắt khách khai lại. Mười ba ngành đều đi chung một bộ não: thêm ngành mới chỉ là thêm một file cấu hình."

Gõ `có laptop nào ngon không`:

> "Còn ngành chưa có dữ liệu thì nói thẳng là chưa có — không đoán bừa một cái tên máy nào."

## Cảnh 5 — Số liệu + kiến trúc (2:25–3:00)

Chiếu bảng: 50/50 tình huống · 100% ô nhu cầu đúng · 0,7 câu hỏi trung bình · 0 hallucination lọt · xử lý ngoài LLM <100ms. Rồi sơ đồ kiến trúc.

> "Toàn bộ đo được, chạy lại được bằng một lệnh — trên cả dữ liệu thật lẫn dữ liệu mẫu công khai. Kiến trúc: LLM chỉ xuất hiện đúng hai chỗ — hiểu lời khách và diễn đạt kết quả. Mọi quyết định là code: lặp lại được, giải trình được, chạy trên hạ tầng model tại Việt Nam qua FPT AI Marketplace — đổi nhà cung cấp bằng một dòng cấu hình. Smart Choice — tư vấn như người bán hàng giỏi nhất của bạn, nhưng không bao giờ bịa."

## Ghi chú quay

- Quay 1 lần liền mạch nếu được — giám khảo tin bản không cắt ghép.
- Zoom chữ to (Ctrl +) trước khi quay. Thử cả dark mode — nếu quay tối thì bật từ đầu, đừng đổi giữa video.
- Chip gợi ý dưới câu trả lời bấm được luôn — dùng nó cho mạch quay nhanh, đỡ gõ.
- Chuẩn bị sẵn phiên dự phòng đã chạy tốt trong tab khác, phòng mạng chậm lúc quay.
- Nếu câu trả lời LLM lượt quay chậm >5s, cắt cảnh chờ, giữ timestamp thống kê ms trên màn hình.
