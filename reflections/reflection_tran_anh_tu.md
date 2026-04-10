# Individual Reflection — Trần Anh Tú

## 1. Role
AI Agent Engineer phụ trách hai agent phức tạp nhất trong pipeline: phân tích sâu điểm mạnh/yếu của ứng viên đối chiếu JD (`CandidateDeepAnalyzer`) và sinh bộ câu hỏi phỏng vấn cá nhân hóa (`InterviewQuestionGenerator`).

## 2. Đóng góp cụ thể
- Viết `src/agents/candidate_deep_analyzer.py` — class `CandidateDeepAnalyzer` với `DeepAnalysisResult` Pydantic model (`strengths`, `weaknesses`), method `analyze()` nhận CV analysis dict và JD analysis dict đã được serialize thành JSON, inject vào prompt để LLM đối chiếu và output điểm mạnh/yếu dạng free-text có cấu trúc.
- Viết `src/agents/interview_question_generator.py` — class `InterviewQuestionGenerator` với smart DB filtering: ưu tiên câu hỏi theo `ten_role` matching với `target_position`, fallback lấy câu hỏi `culture_fit` từ tất cả roles nếu không tìm thấy role phù hợp, giới hạn 30 câu gửi vào prompt để tránh context overflow. Thiết kế `Question` và `InterviewQuestions` Pydantic models.
- Viết 2 system prompts: `candidate_deep_analysis_pt.txt` (role: HR chuyên gia, task: đối chiếu strengths/weaknesses, format: JSON 2 trường) và `interview_question_generator_pt.txt` (role: senior recruiter 10 năm kinh nghiệm, chiến lược chọn câu hỏi kiểm chứng điểm mạnh + khai thác điểm yếu, output: 5 câu hỏi với goal và related_to).

## 3. SPEC mạnh/yếu
- **Mạnh nhất: Use case clarity** — hai prompts được viết với role và task rất cụ thể, không generic. Prompt interview question generator đặc biệt hiệu quả vì có "chiến lược lựa chọn" rõ ràng (verify strength + probe weakness) thay vì chỉ "sinh câu hỏi phỏng vấn". Kết quả: câu hỏi output có tính cá nhân hóa cao hơn hẳn so với template chung.
- **Yếu nhất: Evaluation của output quality** — không có cách đo xem `strengths`/`weaknesses` từ `CandidateDeepAnalyzer` có chính xác không, và 5 câu hỏi phỏng vấn có thực sự phù hợp với ứng viên đó không. Chỉ dùng "cảm quan" của nhóm để đánh giá — đây là điểm yếu lớn nhất khi muốn prove product value.

## 4. Đóng góp khác
- Thiết kế cấu trúc `data/interview_question_db.json` — phân cấp theo `roles` → `questions` → (`cau_hoi`, `loai`), với 4 loại câu hỏi: `teaching`, `technical`, `research`, `culture_fit` — cấu trúc này hỗ trợ smart filtering trong `InterviewQuestionGenerator` theo cả role lẫn question type.
- Test end-to-end flow với `test/test_candidate_deep_analyzer.py` và `test/test_interview_question_generator.py`, phát hiện bug: nếu `strengths` hoặc `weaknesses` là empty string, LLM sinh câu hỏi rất generic — đã fix bằng cách thêm fallback string "Không có thông tin cụ thể" trong prompt.

## 5. Điều học được
Trước hackathon nghĩ "chain of agents" chỉ là gọi nhiều API calls liên tiếp. Sau khi implement mới hiểu: **chất lượng output của agent sau phụ thuộc hoàn toàn vào chất lượng output của agent trước**. Nếu `CandidateDeepAnalyzer` trả về `strengths` chung chung ("có kinh nghiệm AI"), thì `InterviewQuestionGenerator` cũng sinh câu hỏi chung chung. Bài học: trong multi-agent pipeline, cần test từng khâu riêng biệt với mock input chuẩn trước khi test toàn bộ chain.

## 6. Nếu làm lại
Sẽ thêm ít nhất 2-3 câu ví dụ output (few-shot) vào cả hai prompts ngay từ đầu. Trong hackathon hai prompts đều là zero-shot — kết quả khá tốt nhưng đôi khi `weaknesses` viết quá dài và không có cấu trúc nhất quán. Vài-shot examples sẽ enforce format tốt hơn mà không cần thêm code parsing.

## 7. AI giúp gì / AI sai gì
- **Giúp:** Dùng Claude để brainstorm "chiến lược lựa chọn câu hỏi phỏng vấn" cho prompt — Claude gợi ý cụ thể: "chọn câu hỏi verify điểm mạnh" và "chọn câu hỏi probe điểm yếu theo hướng growth mindset thay vì gotcha". Hai chiến lược này được đưa thẳng vào prompt và tạo ra câu hỏi chất lượng hơn hẳn phiên bản đầu.
- **Sai/mislead:** Claude gợi ý thêm trường `follow_up_questions` cho mỗi câu hỏi chính trong `Question` model — về mặt product thì hay nhưng làm tăng gấp đôi token output và schema phức tạp hơn. Khi test thực tế, LLM bắt đầu hallucinate follow-up nếu context không đủ. Quyết định đúng là giữ schema đơn giản với 3 trường: `content`, `goal`, `related_to`.
