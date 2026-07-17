# Lộ trình pilot 3 tháng — Smart Choice × Điện Máy Xanh

> Theo khung pilot đề bài: 1 nhóm ngành hàng thử nghiệm, 1.000–10.000 lượt hội thoại, 3 tháng.

## Tháng 1 — Shadow mode (ngành máy lạnh)

Bot trả lời **song song** với luồng tư vấn hiện tại, không lộ ra khách. Chuyên gia ngành hàng ĐMX chấm mẫu câu trả lời theo 3 trục: hiểu đúng nhu cầu, chất lượng trade-off, độ đúng số liệu.

Việc kỹ thuật: nối API catalog/price/stock/promotion thật thay file tĩnh (adapter đã tách sẵn — chỉ thay tầng nạp); nhận dữ liệu Policy & FAQ để bật nhánh tìm tài liệu (embedding `multilingual-e5-large` + rerank `bge-reranker-v2-m3`, đều có sẵn serverless trên FPT AI Marketplace); bổ sung validator định tính (khẳng định "êm nhất/bền nhất" phải có trục dữ liệu đỡ).

Ngưỡng sang tháng 2: ≥90% câu trả lời được chuyên gia chấm đạt, 0 hallucination nghiêm trọng.

## Tháng 2 — A/B có kiểm soát

Mở cho một phần nhỏ traffic web thật. Đo so với luồng hiện tại: tỷ lệ chuyển đổi sang giỏ hàng, số câu hỏi khách phải trả lời, tỷ lệ khách bỏ giữa chừng, tỷ lệ chuyển nhân viên. Nút "gặp tư vấn viên" luôn hiện — bot không giữ khách.

Song song: gọi thử **FPT STT** thay micro trình duyệt (đồng bộ chất lượng mọi trình duyệt); thử nhập bằng **ảnh** (chụp phòng → gợi ý diện tích, chụp máy cũ → tư vấn nâng cấp; qua Qwen3.6-27B multimodal trên FPT) — ảnh chỉ **điền ô nhu cầu** kèm cờ suy luận và xác nhận của khách, không bao giờ thay catalog làm nguồn số liệu.

## Tháng 3 — Mở rộng ngành

Bật thêm 2–3 ngành từ chính dữ liệu ĐMX (tủ lạnh 1.693 SKU, máy giặt 1.338, tivi...) — mỗi ngành là 1 file config ô nhu cầu + trọng số, không sửa lõi. Fine-tune model trích ô nhu cầu trên hội thoại thật đã gom (LoRA trên FPT AI Factory — dữ liệu không rời hạ tầng Việt Nam).

## Điều kiện ký pilot (đối chiếu yêu cầu đề bài)

| Yêu cầu đề bài | Hiện trạng |
|---|---|
| KPI độ đúng thông tin sản phẩm | Hậu kiểm số theo đơn vị, 0 lọt trên bộ 22 tình huống |
| Không hallucination nghiêm trọng | 4 tầng chắn; đã bắt bịa thật trên demo công khai |
| Giao diện dễ dùng | Chat web + giọng nói, khách không cần biết kỹ thuật |
| Log nguồn dữ liệu | Mỗi con số có badge nguồn: field · nguồn · thời điểm · mã SP |
| Tích hợp API catalog/stock/promotion | Adapter tách sẵn, thay tầng nạp là xong |

## Chi phí vận hành (ước tính)

2 lần chạm LLM/lượt × ~500 token đầu ra → chi phí serverless theo token trên FPT, không thuê GPU cố định. Phần quyết định (lọc/chấm/xếp hạng) chạy code thuần <35ms — chịu tải giờ cao điểm không tốn thêm chi phí model.
