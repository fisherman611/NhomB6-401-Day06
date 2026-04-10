# Individual Reflection — Nguyễn Tiến Thắng

## 1. Role
JD Analysis Engineer kiêm Data Preparation. Phụ trách xây dựng agent phân tích Job Description, thiết kế Pydantic model cho JD, và tạo bộ dữ liệu mock JD phục vụ test toàn nhóm.

## 2. Đóng góp cụ thể
- Viết `src/agents/jd_analyzer.py` — class `JDAnalyzer` với `JDAnalysis` Pydantic model (`job_title`, `years_of_experience`, `technical_skills`, `soft_skills`, `education`, `summary`), implement đầy đủ `analyze()` với structured output + fallback tương tự CVAnalyzer nhưng dành cho JD text.
- Viết `src/models/jd_models.py` — `JDStructuredOutput` Pydantic model chi tiết hơn với `required_skills`, `preferred_skills`, `experience_level`, `key_responsibilities` (3-5 items) — model này phân tách rõ "bắt buộc" vs "ưu tiên" phục vụ thuật toán matching có trọng số.
- Viết `src/prompts/jd_analysis_pt.txt` và tạo `scratch/gen_mock_jds.py` sinh ra 10 JD thực tế (3 domain: AI, CS, Math) bao gồm các cấp độ Junior/Middle/Senior — bộ dữ liệu này được toàn nhóm dùng để test trong suốt hackathon.

## 3. SPEC mạnh/yếu
- **Mạnh nhất: Schema design** — `JDStructuredOutput` có trường `required_skills` và `preferred_skills` tách biệt, trực tiếp phục vụ thuật toán scoring có trọng số (required 70%, preferred 30%) trong `calculate_matching_score()`. Đây là quyết định schema quan trọng tạo ra sự khác biệt so với keyword matching đơn giản.
- **Yếu nhất: Consistency giữa hai models** — `JDAnalysis` (trong jd_analyzer.py) và `JDStructuredOutput` (trong jd_models.py) có cấu trúc khác nhau: `JDAnalysis` dùng `technical_skills` còn `JDStructuredOutput` tách thành `required_skills`/`preferred_skills`. Pipeline thực tế dùng `JDAnalysis` nhưng matching algorithm trong `utils.py` lại expect `required_skills` — gây ra lỗi matching luôn trả về 0.0 trong lần test đầu tiên.

## 4. Đóng góp khác
- Tạo `test/test_jd_analyzer.py` — batch test script phân tích toàn bộ JD trong một thư mục và lưu kết quả JSON ra `data/jd_analysis_results/`, giúp nhóm validate output của JD analyzer nhanh chóng mà không cần chạy full pipeline.
- Debug vấn đề mismatch schema (mô tả ở phần yếu nhất): sau khi phát hiện, phối hợp với Hoàng Văn Bắc để `rank_candidates()` trong `utils.py` dùng đúng field `technical_skills` từ `JDAnalysis` thay vì `required_skills`.

## 5. Điều học được
Trước hackathon không nghĩ đến việc có hai Pydantic models cho cùng một domain object (JD). Sau hackathon mới hiểu: nên có **một model duy nhất** là source of truth, tránh tình trạng hai model song song với field names khác nhau dẫn đến subtle bugs. Bài học về "single source of truth" trong schema design.

## 6. Nếu làm lại
Sẽ thống nhất schema JD ngay từ ngày đầu thay vì có hai versions: `JDAnalysis` cho LLM output và `JDStructuredOutput` là "plan B" chi tiết hơn. Cụ thể: sẽ merge `required_skills` và `preferred_skills` vào `JDAnalysis` ngay từ đầu, đồng thời update prompt để LLM phân biệt hai loại này — tránh được 1-2 tiếng debug mismatch.

## 7. AI giúp gì / AI sai gì
- **Giúp:** Dùng Claude để generate nội dung 10 mock JDs (`scratch/gen_mock_jds.py`) — Claude tạo ra các JD realistic với đầy đủ trách nhiệm, yêu cầu bắt buộc và ưu tiên, tiết kiệm ~1.5 tiếng viết tay. Các JD này đủ đa dạng để test nhiều trường hợp matching.
- **Sai/mislead:** Claude gợi ý thêm trường `salary_range` và `company_culture` vào JDStructuredOutput — phù hợp cho production app nhưng không có CV nào chứa thông tin này để matching, làm tăng độ phức tạp schema mà không có giá trị trong phạm vi hackathon.
