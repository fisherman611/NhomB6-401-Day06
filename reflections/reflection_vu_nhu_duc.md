# Individual Reflection — Vũ Như Đức

## 1. Role
CV Analysis Engineer. Phụ trách xây dựng agent phân tích hồ sơ ứng viên và prompt engineering cho bước trích xuất thông tin CV — đầu vào đầu tiên của toàn bộ pipeline.

## 2. Đóng góp cụ thể
- Viết `src/agents/cv_analyzer.py` — class `CVAnalyzer` với `CVAnalysis` Pydantic model (`full_name`, `years_of_experience`, `technical_skills`, `soft_skills`, `education`, `summary`), method `analyze()` ưu tiên structured output rồi fallback text completion, kèm `_extract_json_object()` xử lý response bọc markdown fence bằng regex.
- Viết `src/prompts/cv_analysis_pt.txt` — prompt 6 phần với bối cảnh JD cụ thể (Senior AI Instructor), hướng dẫn giữ nguyên thuật ngữ tiếng Anh (Python, PyTorch, CNN...), quy tắc ước lượng số năm kinh nghiệm từ timeline, và format output JSON mẫu — qua đó cải thiện độ chính xác trích xuất kỹ năng đáng kể so với prompt generic.
- Thiết kế `CVAnalysis` schema với `ConfigDict(extra="ignore")` để model tự động bỏ qua các field thừa từ LLM response, tránh lỗi validation khi LLM trả về dữ liệu ngoài schema.

## 3. SPEC mạnh/yếu
- **Mạnh nhất: Failure modes** — prompt xử lý rõ trường hợp dữ liệu thiếu (dùng `""` cho text, `[]` cho list, `0` cho số năm kinh nghiệm), kết hợp với `ConfigDict(extra="ignore")` trong Pydantic model tạo thành lớp bảo vệ kép chống crash khi LLM trả về output không hoàn chỉnh.
- **Yếu nhất: Evaluation metrics** — chưa có bộ test case chuẩn để đo accuracy của CV extraction. Không biết prompt trích xuất đúng bao nhiêu % technical skills so với ground truth thực. Chỉ kiểm tra bằng mắt với một vài CV mẫu.

## 4. Đóng góp khác
- Test prompt `cv_analysis_pt.txt` với 5 loại CV khác nhau (senior AI researcher, junior developer, QA engineer, product manager, math lecturer) để xác nhận prompt hoạt động đúng với nhiều profile đa dạng trước khi tích hợp vào pipeline.
- Hỗ trợ Hoàng Văn Bắc debug bước matching: phát hiện vấn đề LLM đôi khi trả về skill dạng "PyTorch/TensorFlow" (chuỗi gộp) thay vì tách riêng — đây là nguyên nhân khiến keyword matching cho điểm thấp hơn thực tế.

## 5. Điều học được
Trước hackathon nghĩ prompt chỉ cần viết ngắn gọn là đủ. Sau khi thử nghiệm mới hiểu: **bối cảnh trong prompt quyết định chất lượng output**. Phiên bản prompt đầu tiên chỉ có "phân tích CV này" cho kết quả trích xuất kỹ năng rất generic. Khi thêm mô tả JD mục tiêu (Senior AI Instructor) vào prompt, LLM tự động ưu tiên trích xuất các kỹ năng liên quan AI/ML — đây là kỹ thuật "prompt grounding" mà trước đó chưa biết tên.

## 6. Nếu làm lại
Sẽ viết ít nhất 3 phiên bản prompt và so sánh output trên cùng một bộ 10 CV mẫu trước khi chọn phiên bản cuối. Trong hackathon chỉ có 1 phiên bản prompt duy nhất và chỉnh sửa incremental — không có điểm baseline để so sánh nên không biết chỉnh sửa nào thực sự cải thiện kết quả.

## 7. AI giúp gì / AI sai gì
- **Giúp:** Dùng Claude để review prompt draft và nhận feedback về các edge case bị bỏ sót — ví dụ case CV không ghi rõ số năm kinh nghiệm mà chỉ có timeline dự án. Claude gợi ý thêm hướng dẫn "ước lượng bảo thủ từ timeline" vào prompt, cải thiện rõ rệt.
- **Sai/mislead:** Claude đề xuất thêm trường `certifications` và `publications` vào `CVAnalysis` schema để capture thêm thông tin — về mặt domain là đúng nhưng làm phức tạp schema và không có downstream consumer nào dùng đến hai trường này trong pipeline hiện tại. Nếu thêm vào sẽ tốn thêm token mà không tạo ra giá trị.
