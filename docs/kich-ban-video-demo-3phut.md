# SmartChoiceAI — Kịch bản video demo 3 phút

Tổng thời lượng: 180 giây. Định dạng: quay màn hình (screen record) + lời bình đọc chồng (voiceover). Giọng đọc: nam/nữ trung tính, tốc độ vừa (~150 từ/phút). Con trỏ chuột đi chậm, dừng 1 nhịp trước mỗi cú bấm để người xem kịp thấy.

Chuẩn bị trước khi quay:
- Đã chạy `deploy.ps1` (bản mới nhất) và VPS có khóa FPT (để hiện đủ trích nhu cầu, thị giác, giọng nói).
- Mở sẵn 2 tab: (1) `demo.aibutler.vn` (landing), (2) một ảnh nhãn năng lượng / ảnh máy cũ để kéo thả thử thị giác.
- Xoá hội thoại cũ để mở màn sạch. Thu ở 1920×1080, ẩn thanh bookmark.

Ký hiệu: [HÌNH] = thao tác/hình trên màn hình · [ĐỌC] = lời bình đọc chồng · [CHỮ] = chữ overlay gợi ý.

---

## Cảnh 1 — Mở màn & vấn đề (0:00 – 0:12)

[HÌNH] Trang landing `demo.aibutler.vn` hiện ra, cuộn nhẹ qua khối "Hiểu nhu cầu thật / So sánh khách quan / Nguồn minh bạch".

[ĐỌC] "Mua điện máy, ai cũng gặp một câu hỏi: máy nào hợp với mình? Chatbot thường chào hỏi lan man, hoặc tệ hơn — bịa giá, bịa thông số. SmartChoiceAI làm khác."

[CHỮ] SmartChoiceAI · Tư vấn theo nhu cầu thật · Mọi con số đều có nguồn

---

## Cảnh 2 — Landing dữ liệu thật (0:12 – 0:33)

[HÌNH] Cuộn tới "Tư vấn theo danh mục" — rê qua các thẻ Máy lạnh, Tủ lạnh, Máy sấy… (ảnh khớp đúng ngành). Cuộn tiếp tới khối khuyến mãi: 4 thẻ Aqua −51%, Midea −40%, Casper −33%, Funiki −29%.

[ĐỌC] "Toàn bộ landing chạy trên catalog thật của Điện Máy Xanh: mười bốn ngành, hơn hai nghìn sản phẩm. Không có ảnh mẫu, không có giá bịa — mỗi khuyến mãi là giá gốc trừ giá bán lấy thẳng từ dữ liệu."

[HÌNH] Bấm nút "Tư vấn máy này" trên một thẻ → chuyển sang trang chat, câu hỏi tự điền và gửi.

[ĐỌC] "Bấm tư vấn, hệ thống mở trợ lý chat với đúng sản phẩm đó."

---

## Cảnh 3 — Hiểu nhu cầu đời thường, hỏi giá trước (0:33 – 1:05)

[HÌNH] Về trang chat sạch. Gõ: `nhà 20m² muốn mua máy lạnh mát nhanh, tầm 10 triệu`. Gửi.

[ĐỌC] "Khách nói bằng ngôn ngữ đời thường — không cần thuật ngữ. Trợ lý bắt ngay diện tích, ưu tiên và ngân sách."

[HÌNH] Trợ lý trả về top 3 máy lạnh, mỗi thẻ có giá gạch, phần trăm giảm, và các badge nguồn tên tiếng Việt; kèm dòng "được gì / mất gì".

[ĐỌC] "Kết quả là ba máy phù hợp nhất, kèm điểm mạnh và điểm yếu từng máy — chứ không phải máy nào cũng khen tốt. Và trợ lý hỏi giá trước, đúng cách người thật hay hỏi, chứ không bắt khai số kg hay thông số kỹ thuật."

[CHỮ] Top 3 · trade-off từng máy · giá & tồn kho từ DB

---

## Cảnh 4 — Điểm nhấn: chống bịa & minh bạch (1:05 – 1:32)

[HÌNH] Bấm mở khối "🔍 AI đã làm gì trong câu này?" dưới một câu trả lời. Panel bung ra: AI làm gì / code làm gì / đã chặn bịa.

[ĐỌC] "Đây là điểm khác biệt lớn nhất. Mỗi câu trả lời đều mở được bảng minh bạch: phần nào do AI hiểu ngôn ngữ, phần nào do thuật toán quyết định. Giá, tồn kho, xếp hạng — luôn do code tính, không để mô hình tự chế."

[HÌNH] Bấm vào một badge nguồn trên con số (ví dụ giá) → hiện trường, nguồn, thời điểm, mã sản phẩm.

[ĐỌC] "Bấm vào bất kỳ con số nào, nó truy ngược ra nguồn: trường dữ liệu, thời điểm, mã sản phẩm. Không có con số nào không có gốc."

---

## Cảnh 5 — Suy luận thông minh nhưng an toàn (1:32 – 1:58)

[HÌNH] Gõ: `tóc tôi khô lâu thì nên mua gì`. Gửi.

[ĐỌC] "Thử một câu đánh đố. Khách tả tình huống, không gọi tên sản phẩm."

[HÌNH] Trợ lý trả lời: nhận ra đang cần máy sấy tóc, nhưng thành thật báo chưa có dữ liệu ngành đó, và liệt kê 14 ngành đang tư vấn được.

[ĐỌC] "Trợ lý suy ra được là máy sấy tóc — nhưng vì mặt hàng này chưa có trong dữ liệu, nó từ chối thẳng thay vì bịa một sản phẩm gần đúng. Thông minh, nhưng biết điểm dừng."

[CHỮ] Suy luận có kiểm soát · thà nói 'chưa có' còn hơn bịa

---

## Cảnh 6 — Đa phương thức: chụp ảnh & giọng nói (1:58 – 2:22)

[HÌNH] Bấm nút 📷, chọn ảnh nhãn năng lượng (hoặc ảnh máy cũ). Trợ lý đọc ra thông số từ ảnh và đưa vào tư vấn.

[ĐỌC] "Không chỉ gõ chữ. Khách chụp ảnh nhãn năng lượng hay chiếc máy cũ — mô hình thị giác đọc thông số rồi đưa vào đúng luồng tư vấn, và con số vẫn qua bước hậu kiểm."

[HÌNH] Bấm nút loa/đọc trên một câu trả lời → nghe giọng tiếng Việt, mặt trợ lý nhép miệng theo.

[ĐỌC] "Và trợ lý trả lời bằng giọng tiếng Việt — nói, nghe, nhìn, đủ cả."

---

## Cảnh 7 — Giải trình & khả năng nhân rộng (2:22 – 2:45)

[HÌNH] Gõ: `vì sao chọn máy đầu tiên`. Trợ lý trả về bảng điểm giải trình từng tiêu chí.

[ĐỌC] "Hỏi vì sao chọn máy này, nó không chống chế — mà mở bảng điểm đúng công thức code đã tính. Tự giải trình chính mình."

[HÌNH] Cuộn nhanh qua thanh danh mục 14 ngành (máy lạnh, tủ lạnh, máy giặt, máy sấy, tủ đông, máy rửa chén, máy nước nóng, màn hình, tablet…).

[ĐỌC] "Toàn bộ tri thức mỗi ngành nằm trong một file cấu hình — thêm ngành mới chỉ là thêm một file, không sửa lõi."

---

## Cảnh 8 — Kết (2:45 – 3:00)

[HÌNH] Màn hình kết: logo SmartChoiceAI + 3 dòng số liệu chạy lên.

[ĐỌC] "Một trăm hai mươi bài kiểm thử tự động đều xanh. Xử lý ngoài mô hình dưới một trăm mili-giây. Và số ca bịa lọt qua kiểm chứng: bằng không. SmartChoiceAI — trợ lý AI tư vấn theo nhu cầu thật, nơi mọi con số đều có nguồn."

[CHỮ]
- 14 ngành · 2.176 sản phẩm thật
- 120 test xanh · 0 hallucination · < 100ms
- SmartChoiceAI · demo.aibutler.vn

---

## Ghi chú sản xuất

- Nếu 3 phút hơi chật, cắt bớt Cảnh 6 (giọng nói) còn một nửa, hoặc gộp Cảnh 7 vào Cảnh 8.
- Quay từng cảnh riêng rồi ghép; câu gõ nên chuẩn bị sẵn để dán (paste) cho mượt, tránh gõ sai trên hình.
- Nếu chưa cấu hình khóa FPT: thị giác và giọng nói (Cảnh 6) sẽ không chạy — thay bằng cảnh so sánh hai máy (`so sánh máy 1 và máy 2`) để vẫn đủ 3 phút.
- Tổng lời bình ~420 từ, khớp ~180 giây ở tốc độ đọc vừa.
