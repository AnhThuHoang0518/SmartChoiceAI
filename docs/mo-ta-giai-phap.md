# SmartChoiceAI — Mô tả giải pháp

## 1. Tóm tắt

SmartChoiceAI là một AI Agent tư vấn điện máy hội thoại tiếng Việt, đa phương thức: khách nói, gõ, hoặc chụp ảnh; agent hiểu nhu cầu bằng ngôn ngữ đời thường, chủ động hỏi lại đúng vài câu quyết định, rồi đề xuất top 3 sản phẩm kèm lý do và điểm mạnh–yếu từng máy, đọc lại bằng giọng tiếng Việt. Toàn bộ đề xuất neo trên catalog thật của Điện Máy Xanh — 14 ngành hàng, 2.176 sản phẩm — và mọi con số đều truy được về nguồn.

Sản phẩm là AI-first theo bản chất: nó phối hợp đồng thời năm loại mô hình AI (LLM hiểu ngôn ngữ, LLM diễn đạt, thị giác đọc ảnh, giọng nói STT/TTS, embedding hiểu ý mờ) và hai cơ chế truy hồi có kiểm soát (tra cứu chính sách theo tài liệu, truy hồi ngữ nghĩa bằng vector) trong một vòng lặp agent: Nhận thức → Suy luận → Hành động → Tự kiểm chứng.

## 2. Triết lý AI-native có trách nhiệm

Điểm khác biệt cốt lõi: chúng tôi dùng AI đúng chỗ, không dùng AI bừa. Trong mỗi lượt, LLM chỉ chạm hai điểm khó nhất mà chỉ AI làm được — hiểu câu tiếng Việt lộn xộn và diễn đạt kết quả tự nhiên. Việc cần tuyệt đối không sai — giá, tồn kho, xếp hạng, chính sách — do thuật toán tường minh và tài liệu gốc quyết định, và chính AI viết ra bộ thuật toán đó. Một trợ lý AI bịa giá hay bịa điều khoản bảo hành là vô dụng; đây là lựa chọn AI-native trưởng thành, không phải né dùng AI.

Cách này triệt tiêu ba lỗi kinh điển ngay từ kiến trúc, không phải bằng lời nhắc trong prompt: trôi hội thoại (LLM tự dẫn thì hỏi lan man, quên nhu cầu ban đầu), bịa dữ liệu, và khen sản phẩm nào cũng tốt. Toàn bộ hệ hơn 6.000 dòng code backend được xây dựng qua cộng tác người–AI; con người định hướng nghiệp vụ, AI đảm nhận kỹ thuật.

## 3. Truy hồi có kiểm soát: RAG nhưng thay khâu sinh bằng trích nguồn

Hệ có đầy đủ khâu truy hồi của một pipeline RAG, nhưng chủ động thay khâu "sinh tự do" bằng trả lời có nguồn, vì đây là chỗ LLM dễ bịa nhất.

Truy hồi tài liệu (lexical). Với câu hỏi chính sách — bảo hành, đổi trả, giao hàng, lắp đặt, khui hộp Apple, dữ liệu cá nhân — hệ nạp bảy tài liệu thật của đối tác ở runtime, tách thành đoạn, chấm điểm theo từ khóa và tiêu đề, rồi trả về chính đoạn văn gốc kèm tên tài liệu. Không một câu chữ nào do LLM sinh ra ở đây; thiếu tài liệu thì nói thẳng là chưa có, không đoán. Tài liệu gốc nằm ngoài git để bảo mật, chỉ nạp khi máy chủ chạy.

Truy hồi ngữ nghĩa (vector). Khi khách nói mục đích mà không gọi tên sản phẩm ("cho con học online", "giữ đồ đông lạnh bán hàng"), hệ dùng embedding tiếng Việt biến câu thành vector, so cosine với vector đại diện của mười ba ngành đã tính sẵn, và đề xuất ngành gần nghĩa nhất dưới dạng chip để khách bấm. Đây là tìm kiếm tương đồng ngữ nghĩa thật sự, nhưng chỉ dùng để định tuyến ý — không tự chốt ngành, không tự đặt ngưỡng, không sinh câu trả lời từ vector. Không có khóa mô hình thì lớp này trả rỗng và hệ lui về luật từ khóa, hành vi cũ giữ nguyên.

## 4. Workflow: hành trình một tin nhắn

Mỗi câu khách gửi đi qua một pipeline cố định, phần lớn là code, LLM chỉ chen vào hai điểm.

Bước 1 — Bảo mật đầu vào. Nhận diện và che số điện thoại trước khi xử lý, tránh lộ dữ liệu cá nhân và tránh nhầm số điện thoại thành số tiền.

Bước 2 — Chuẩn hóa tiếng Việt (code). Bung viết tắt, hiểu không dấu, sửa lỗi chính tả nhẹ, quy đổi tiền (20tr, mười lăm triệu, triệu rưỡi), phép tính đơn giản (phòng 3m x 4m thành 12m²), và code-switching Việt–Anh.

Bước 3 — Truy hồi chính sách. Nếu là câu hỏi chính sách hay dịch vụ, hệ rẽ ngay sang tra cứu tài liệu ở mục 3 và trả đoạn gốc có nguồn, không đi tiếp xuống luồng tư vấn.

Bước 4 — Nhận thức nhu cầu (LLM #1). Luật regex trích trước những gì chắc chắn; LLM chỉ vớt phần còn thiếu và điền vào JSON theo schema riêng từng ngành. Đầu ra sai schema bị loại và trích lại — LLM không được tư vấn hay thêm chữ ở lớp này.

Bước 5 — Định tuyến ngành. Xác định khách cần ngành nào trong 14 ngành. Ba cơ chế chồng lên nhau: khớp từ khóa, loại-trừ va chạm (máy sấy tóc không nhầm máy sấy quần áo, quạt điều hòa không nhầm máy lạnh, tủ đông trùng tự động sau khi bỏ dấu), và truy hồi ngữ nghĩa bằng embedding cho nhu cầu gián tiếp. Sản phẩm suy ra mà không có dữ liệu thì từ chối thật thà.

Bước 6 — Nhận diện ý phụ (khoảng 20 loại). Trước khi vào luồng tư vấn chính, agent bắt nhiều ý: giải thích kiến thức (Inverter khác gì), hỏi dịch vụ, hỏi giá một hãng, so sánh hai máy, vì sao chọn máy này, khuyến mãi, tồn kho, tiêu chí chủ quan, phủ định hãng, nhu cầu mâu thuẫn, đa ý nhiều ngành. Mỗi ý một xử lý riêng, tất cả bằng code hoặc dữ liệu.

Bước 7 — Suy luận, hỏi ngược thông minh (code). Máy trạng thái phía server giữ nhu cầu qua các lượt. Nếu chưa đủ ô bắt buộc, hệ đo giá trị thông tin: mô phỏng từng ô trống nhận các giá trị khác nhau thì top 3 lệch bao nhiêu, chỉ hỏi câu làm thay đổi kết quả. Trung bình dưới một câu hỏi để ra tư vấn.

Bước 8 — Hành động: lọc và xếp hạng (code). Lọc cứng theo công bố của hãng và ngân sách. Chấm điểm mềm với trọng số sinh từ chính ưu tiên khách nói. Ra top 3, mỗi máy kèm trade-off được gì / mất gì, và chủ động nêu vì sao không đề xuất máy khách đang nhắm.

Bước 9 — Diễn đạt (LLM #2). LLM nhận bảng kết quả đã tính xong và viết lại cho dễ nghe. Nó không thấy catalog, không biết máy nào khác tồn tại, nên không có gì để bịa.

Bước 10 — Tự kiểm chứng (code). Hậu kiểm quét mọi con số có đơn vị trong bản nháp LLM, đối chiếu ngược theo từng rổ đơn vị (khoảng 30 rổ). Số bịa bị chặn, bắt viết lại; quá ngưỡng thì rơi về bản dự phòng mà mọi số đều thật. Mỗi con số hiển thị bấm được ra nguồn: trường, nguồn, thời điểm, mã sản phẩm.

## 5. Đa phương thức và giải trình

Khách chụp ảnh nhãn năng lượng hay máy cũ — mô hình thị giác đọc ra thông số, đưa vào đúng pipeline trên (ảnh chỉ điền ô nhu cầu, số vẫn qua hậu kiểm). Khách nói bằng giọng — nhận giọng rồi trả lời bằng giọng đọc tiếng Việt, mặt trợ lý nhép miệng theo. Giao diện có bảng "AI đã làm gì trong câu này?" phơi bày minh bạch từng bước AI so với code cho mỗi câu trả lời — biến kiến trúc chống-bịa thành điểm phô diễn. Trang danh mục trên landing cũng lấy sản phẩm thật từ catalog, lọc hãng và giá chạy trên dữ liệu thật, không có sản phẩm mẫu. Agent còn tự lập kế hoạch nhiều bước (khách nói máy lạnh và tủ lạnh thì tư vấn xong máy lạnh tự đề xuất xem tiếp tủ lạnh) và tự giải trình chính mình (hỏi vì sao chọn máy này thì trả lời bằng bảng điểm code đã tính).

## 6. Kết quả và khả năng nhân rộng

Toàn bộ tri thức ngành nằm trong file cấu hình — thêm ngành mới chỉ là thêm một file config, không sửa lõi. Hệ chạy trên dữ liệu thật, đo được và tái lập bằng một lệnh: 74 tình huống tự động, 102 unit test, và bộ câu tấn công đều xanh, trên cả dữ liệu thật lẫn dữ liệu mẫu công khai; 100% ô nhu cầu trích đúng; xử lý ngoài LLM dưới 100ms; 0 hallucination lọt qua hậu kiểm. Adapter cho phép đổi nhà cung cấp mô hình bằng một dòng cấu hình, ưu tiên hạ tầng AI tại Việt Nam — không khóa cứng vào một API nước ngoài, và khi mô hình gặp sự cố hệ vẫn chạy đủ luồng, chỉ kém phần diễn đạt.
