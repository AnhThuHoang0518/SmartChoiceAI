# SmartChoiceAI — Mô tả giải pháp

## 1. Vấn đề và tóm tắt

Khách mua điện máy hiếm khi đọc bảng thông số. Họ nói bằng ngôn ngữ đời thường — "máy lạnh dưới 20 triệu cho phòng ngủ 18m² tiết kiệm điện", thậm chí chỉ mô tả tình huống "nhà nóng quá", "tóc bị ướt cần mua gì". Các trang so sánh hiện nay bắt khách tự lọc theo cột kỹ thuật, còn chatbot thường thì hay bịa giá, quên nhu cầu giữa chừng.

SmartChoiceAI là một trợ lý AI hội thoại tiếng Việt: nghe khách mô tả nhu cầu, chủ động hỏi lại đúng vài câu quyết định, rồi đề xuất top 3 sản phẩm kèm lý do và điểm mạnh–yếu của từng máy, bằng ngôn ngữ bình dân — và **mọi con số đều truy được về catalog thật của Điện Máy Xanh**.

## 2. Nguyên tắc lõi: LLM chỉ chạm hai điểm

Điểm khác biệt cốt lõi: **LLM không cầm lái**. Trong mỗi lượt chat, mô hình ngôn ngữ chỉ làm đúng hai việc — (1) trích nhu cầu khách thành JSON, và (2) diễn đạt kết quả đã tính sẵn thành lời tư vấn. Việc chọn hỏi gì, lọc gì, xếp hạng ra sao đều do **thuật toán tường minh** quyết định.

Đây là cách duy nhất vừa chống trôi hội thoại, vừa chống bịa số, vừa giải trình được từng khuyến nghị. Chúng tôi triệt tiêu ba lỗi kinh điển của chatbot tư vấn ngay từ kiến trúc, không phải bằng lời nhắc trong prompt: **trôi flow** (để LLM tự dẫn thì nó hỏi lan man, quên nhu cầu ban đầu); **bịa dữ liệu** (tự chế giá, tồn kho, khuyến mãi); và **nói sản phẩm nào cũng tốt** (không dám nêu nhược điểm nên vô dụng).

## 3. Kiến trúc ba lớp

**Lớp Hiểu.** Chuẩn hóa tiếng Việt mua sắm thật: không dấu, viết tắt ("đth/tk điện/đt"), lỗi chính tả, code-switching Việt–Anh, đơn vị m²/HP/BTU/GB/lít/inch, số viết bằng chữ ("mười lăm triệu"), phép tính đơn giản ("phòng 3m x 4m" → 12m²). LLM trích JSON theo schema riêng từng ngành; đầu ra sai schema thì bị loại và trích lại.

**Lớp Quyết định (code, không LLM).** Máy trạng thái lưu nhu cầu phía server. Mỗi lượt, code kiểm: đủ thông tin chưa? Nếu chưa, chọn đúng một câu hỏi đáng giá nhất. Nếu đủ, chạy lọc cứng rồi chấm điểm để ra top 3.

**Lớp Diễn đạt.** LLM nhận bảng kết quả đã tính xong và viết lại cho dễ nghe. Nó không được thêm số nào ngoài dữ liệu đưa vào; đầu ra bị hậu kiểm trước khi tới khách.

Toàn bộ tri thức ngành nằm trong file cấu hình. Thêm ngành mới chỉ là thêm một file config — không sửa lõi.

## 4. Chống bịa bằng cơ chế

Đề bài cấm bịa giá/tồn kho/khuyến mãi. Prompt "đừng bịa nhé" chỉ là lời khuyên; chúng tôi làm **cơ chế**. Hậu kiểm quét mọi con số có đơn vị trong bản nháp của LLM, đối chiếu ngược theo từng rổ đơn vị (khoảng 30 rổ: tiền, dB, kWh, lít, inch, mAh…). Bài học thực tế: "18 hợp lệ ở rổ m² không được bảo lãnh cho '18 dB'" — nên mỗi đơn vị một rổ riêng. Số bịa bị chặn, bắt viết lại; quá ngưỡng thì rơi về bản dự phòng template mà mọi số đều thật. Mỗi con số trên giao diện đều bấm được ra nguồn: trường nào, lấy từ đâu, thời điểm, mã sản phẩm.

## 5. Hỏi ngược thông minh

Với mỗi ô còn trống, hệ mô phỏng: nếu ô này nhận các giá trị khác nhau, top 3 đổi bao nhiêu? Đổi nhiều thì hỏi; không đổi thì bỏ qua, không làm phiền khách. Ví dụ phòng 18m² thì "có nắng không" được điểm 1,00 (hỏi ngay, vì nắng đẩy sang dải máy khác), còn "phòng ngủ hay khách" chỉ ảnh hưởng độ ồn nên cân nhắc sau. Kết quả: trung bình dưới một câu hỏi để ra tư vấn.

## 6. Hiểu tiếng Việt sâu và trung thực

Hệ nhận diện nhiều lớp ngôn ngữ đời thường: phủ định hãng ("không phải LG" → loại LG, không hiểu ngược), nhu cầu mâu thuẫn ("cao cấp nhất nhưng rẻ nhất" → hỏi ưu tiên), câu hỏi kiến thức ("Inverter khác gì?" → giải thích rồi kéo về nhu cầu), và **nhu cầu gián tiếp** ("tóc bị ướt" → máy sấy tóc). Đặc biệt, khi suy ra sản phẩm không có trong dữ liệu, hệ **từ chối thật thà** thay vì đẩy bừa sang ngành gần giống — "máy sấy tóc" không bị nhầm thành "máy sấy quần áo". Cơ chế loại-trừ từ khóa cũng chặn các va chạm như "quạt điều hòa" (không phải máy lạnh) hay "tủ đông" trùng "tự động" sau khi bỏ dấu.

## 7. AI-native đa phương thức

Sản phẩm dùng đồng thời sáu năng lực AI, mỗi loại ở đúng chỗ nó giỏi: LLM hiểu ngôn ngữ, LLM diễn đạt, giọng đọc TTS tiếng Việt, nhận giọng nói STT, thị giác đọc ảnh (khách chụp nhãn năng lượng hay máy cũ, AI đọc ra thông số), và embedding hiểu mục đích mờ. Giao diện có bảng "AI đã làm gì trong câu này?" phơi bày minh bạch từng bước AI so với code — biến kiến trúc chống-bịa thành điểm phô diễn thay vì điểm yếu.

## 8. Tính agent và giải trình

Hệ tự lập kế hoạch khi khách nói nhiều nhu cầu ("máy lạnh… và tủ lạnh…" → tư vấn máy lạnh xong tự đề xuất xem tiếp tủ lạnh), tự dẫn khách qua từng bước tới quyết định, và **tự giải trình được chính mình**: hỏi "vì sao chọn máy này?" thì trả lời bằng bảng điểm code đã tính — trục nào bao nhiêu, trọng số sinh từ ưu tiên khách nói — không cảm tính, không nhờ AI chấm.

## 9. Dữ liệu thật và kết quả

Chạy trên dữ liệu thật của Điện Máy Xanh: **14 ngành hàng, 2.176 sản phẩm**, ảnh chính chủ đối chiếu qua mã sản phẩm. Toàn bộ đo được và chạy lại bằng một lệnh: **74 tình huống tự động + 90 unit test + 23 câu tấn công đều xanh**, trên cả dữ liệu thật lẫn dữ liệu mẫu công khai; 100% ô nhu cầu trích đúng; xử lý ngoài LLM dưới 100ms; 0 hallucination lọt qua hậu kiểm. Adapter cho phép đổi nhà cung cấp mô hình bằng một dòng cấu hình, ưu tiên hạ tầng AI tại Việt Nam — không khóa cứng vào một API nước ngoài.
