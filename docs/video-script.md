# Kịch bản video demo — 1 shot, 3 phút

> Quay **một lần liên tục, không cắt cảnh**: 1 file video, 1 lần bấm record,
> giữ nguyên tab trình duyệt https://demo.aibutler.vn từ đầu đến cuối. Lồng
> tiếng đọc trực tiếp trong lúc quay (hoặc thu riêng rồi ghép — nhưng hành
> động trên màn hình phải khớp giây với lời đọc bên dưới). Đọc với tốc độ
> vừa phải sẽ vừa đúng 3:00. Toàn bộ thao tác gõ/bấm liệt kê theo đúng thứ
> tự thực hiện — không nhảy tab, không refresh, không dừng quay giữa chừng.

## Chuẩn bị trước khi bấm record

- Mở sẵn https://demo.aibutler.vn ở `/chat`, zoom trình duyệt to chữ (Ctrl +).
- Chọn 1 theme (sáng hoặc tối) và giữ nguyên suốt video.
- Mở sẵn 1 phiên chat dự phòng ở tab ẩn (phòng mạng chậm) — không đụng tới
  nếu tab chính chạy mượt.
- Tắt thông báo, để màn hình sạch, con trỏ chuột không nhấp nháy linh tinh.
- Micro test trước — lồng tiếng phải rõ hơn tiếng gõ phím.

## Dòng thời gian liên tục (00:00 → 03:00)

**00:00–00:20 — Mở đầu, đặt vấn đề**
Màn hình: trang chủ demo, có thể lướt nhanh qua bảng thông số kiểu cũ (RAM/BTU/dB) trước khi bấm vào khung chat.

> "Khách mua điện máy không cần bảng thông số — họ cần biết máy nào hợp với nhu cầu THẬT của họ. Smart Choice hỏi đúng vài câu quyết định rồi tư vấn bằng ngôn ngữ người thường, trên dữ liệu thật của Điện Máy Xanh: 14 ngành hàng, 2.176 sản phẩm đang bán."

**00:20–01:05 — Câu hỏi mẫu của đề bài**
Thao tác: gõ trực tiếp vào ô chat, không dừng quay: `e muon mua may lanh duoi 20tr cho phong 18m2, tk dien, it on`, bấm gửi.

> "Viết tắt, không dấu — hệ thống vẫn hiểu: ngân sách 20 triệu, phòng 18 mét vuông, ưu tiên tiết kiệm điện và ít ồn. Nó KHÔNG hỏi cả đống — chỉ hỏi câu làm thay đổi kết quả."

Thao tác: khi bot hỏi lại, trỏ chuột vào dòng "Vì sao hỏi câu này: co_nang = 1.00" — không bấm gì, chỉ di chuột chỉ vào.

> "Mỗi câu hỏi có điểm số. Nắng chiều làm đổi toàn bộ danh sách máy phù hợp — nên nó hỏi. Phòng ngủ hay phòng khách với ca này không đổi kết quả — nên nó không làm phiền."

Thao tác: gõ trả lời `co, chieu nang lam`, gửi, đợi top 3 hiện ra.

> "Top 3, mỗi máy nói rõ ĐƯỢC gì — MẤT gì: rẻ hơn, êm hơn, chịu thiệt chỗ nào. Máy đang khuyến mãi hiện giá gốc gạch và mức giảm THẬT. Và dòng 'Vì sao em không đề xuất' — máy quảng cáo giá tốt nhưng thiếu tải cho phòng có nắng. Tư vấn thật là dám nói câu đó."

**01:05–01:45 — So sánh trực tiếp + chống bịa**
Thao tác: bấm nút **⚖ So sánh với máy 1** trên card máy thứ 2, đợi bảng so sánh hiện.

> "Đề bài tên là 'so sánh sản phẩm' — đây: bảng đối chiếu từng thông số, kết luận rẻ hơn bao nhiêu tiền. Bảng này do CODE dựng từ dữ liệu có nguồn, không qua model sinh chữ — nên không thể bịa và trả về tức thì."

Thao tác: bấm badge ⓘ cạnh dòng Giá, đợi popup nguồn dữ liệu hiện.

> "Mọi con số truy được về nguồn: trường nào, API nào, lấy lúc nào, mã sản phẩm nào. Còn khi model định nói một số KHÔNG có trong dữ liệu — dòng 'đã chặn bịa' này — nó bị chặn và bắt viết lại. Chống hallucination là cơ chế chạy từng câu, không phải lời hứa trong slide."

**01:45–02:25 — Giọng nói, đổi ý giữa chừng, đổi ngành**
Thao tác: bấm icon 🎤, nói rõ vào micro: "nếu giảm còn mười lăm triệu thì sao", đợi hệ thống nhận diện và trả lời.

> "Nói bằng giọng — và khách vừa ĐỔI ngân sách giữa chừng: hệ thống ghi đè đúng ô đó, giữ mọi thứ đã biết, tính lại từ đầu."

Thao tác: gõ `thế còn tủ lạnh thì sao`, gửi.

> "Đổi hẳn ngành giữa cuộc nói chuyện — nó chuyển sang tủ lạnh và MANG ngân sách 15 triệu theo, không bắt khách khai lại. Mười bốn ngành đều đi chung một bộ não: thêm ngành mới chỉ là thêm một file cấu hình."

Thao tác: gõ `co laptop nao ngon khong`, gửi.

> "Còn ngành chưa có dữ liệu thì nói thẳng là chưa có — không đoán bừa một cái tên máy nào."

**02:25–03:00 — Số liệu + kiến trúc, chốt**
Thao tác: cuộn xuống hoặc chuyển sang tab đã mở sẵn bảng số liệu đánh giá + sơ đồ kiến trúc (mở sẵn từ trước, chỉ cần chuyển tab trong cùng cửa sổ, không dừng quay).

> "Toàn bộ đo được, chạy lại được bằng một lệnh — trên cả dữ liệu thật lẫn dữ liệu mẫu công khai: 50 trên 50 tình huống đúng, 100% ô nhu cầu trích đúng, trung bình 0,7 câu hỏi mỗi phiên, 0 hallucination lọt, phần xử lý ngoài LLM dưới 100 mili giây."

> "Kiến trúc: LLM chỉ xuất hiện đúng hai chỗ — hiểu lời khách và diễn đạt kết quả. Mọi quyết định là code: lặp lại được, giải trình được, chạy trên hạ tầng model tại Việt Nam qua FPT AI Marketplace — đổi nhà cung cấp bằng một dòng cấu hình. Smart Choice — tư vấn như người bán hàng giỏi nhất của bạn, nhưng không bao giờ bịa."

Dừng quay ở đúng 03:00.

## Ghi chú quay 1 shot

- Không cắt, không ghép hậu kỳ — giám khảo tin bản không chỉnh sửa. Nếu hỏng
  giữa chừng, quay lại từ đầu, không nối 2 đoạn.
- Tập đọc lời thoại to trước 1–2 lần cho khớp nhịp với thao tác, vì mỗi câu
  đọc phải trùng lúc thao tác đang diễn ra trên màn hình, không đọc trước
  hoặc sau hành động quá xa.
- Chip gợi ý dưới câu trả lời bấm được luôn — ưu tiên bấm chip thay vì gõ tay
  ở đoạn nào chip có sẵn đúng ý, để rút ngắn thời gian gõ.
- Nếu một lượt trả lời của LLM chậm quá 5 giây, cứ để nguyên trong bản quay
  (không cắt cảnh chờ vì đây là 1 shot) — giữ đúng tinh thần "video thật,
  không dàn dựng"; nếu cần, chọn trước câu hỏi/thời điểm mạng ổn định.
- Phiên dự phòng ở tab ẩn chỉ dùng khi tab chính lỗi thật sự — nếu phải
  chuyển tab, đó vẫn tính là quay lại từ đầu, không dùng đoạn đã quay dở.
