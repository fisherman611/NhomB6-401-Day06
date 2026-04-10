# Individual Reflection — Nguyễn Như Giáp

## 1. Role
Team Lead kiêm Pipeline Architect. Phụ trách thiết kế kiến trúc tổng thể của project và viết `main.py` — điểm điều phối toàn bộ pipeline 5 bước từ phân tích JD đến hiển thị kết quả cuối cùng.

## 2. Đóng góp cụ thể
- Thiết kế cấu trúc thư mục project (`src/agents`, `src/engine`, `src/models`, `src/prompts`, `ui`, `test`, `scratch`, `data`) và định nghĩa trách nhiệm của từng layer để 6 thành viên khác có thể làm việc song song mà không xung đột.
- Viết `main.py` — pipeline CLI 5 bước: (1) khởi tạo services & agents, (2) phân tích JD, (3) phân tích hàng loạt CV, (4) ranking Top-N, (5) deep analysis + sinh câu hỏi phỏng vấn — có output JSON ra file `data/final_pipeline_results.json`.
- Tích hợp toàn bộ 4 agents (`CVAnalyzer`, `JDAnalyzer`, `CandidateDeepAnalyzer`, `InterviewQuestionGenerator`) và hàm `rank_candidates` từ `src/utils.py` vào một luồng end-to-end chạy được từ dòng lệnh.

## 3. SPEC mạnh/yếu
- **Mạnh nhất: System design** — phân tách rõ ràng từng bước trong pipeline, mỗi agent chỉ làm một việc, dễ thay thế hoặc nâng cấp từng thành phần mà không phá vỡ toàn bộ hệ thống. Đây là nền tảng để nhóm phân công công việc và chạy thử độc lập.
- **Yếu nhất: ROI & deployment planning** — pipeline mới chạy được dưới dạng script CLI, chưa có logic xử lý lỗi ở cấp độ từng batch CV (nếu một CV lỗi, pipeline có thể dừng toàn bộ). Chưa ước tính được thời gian xử lý khi scale lên hàng trăm CV.

## 4. Đóng góp khác
- Debug vấn đề `ModuleNotFoundError` khi các thành viên chạy agent trực tiếp, từ đó chuẩn hóa pattern thêm `PROJECT_ROOT` vào `sys.path` — pattern này được áp dụng nhất quán ở tất cả 4 agent files.
- Hỗ trợ Hoàng Văn Bắc kết nối `rank_candidates()` vào `main.py` sau khi hàm `calculate_matching_score()` v1 có thể chạy được, đảm bảo output đúng schema để deep agent xử lý tiếp.

## 5. Điều học được
Trước hackathon nghĩ rằng phân chia công việc cứ "chia đều theo số file" là đủ. Qua hackathon mới hiểu: điểm nghẽn không phải ở số lượng file mà ở **interface giữa các module** — nếu schema đầu ra của `CVAnalyzer` không khớp với đầu vào của `CandidateDeepAnalyzer`, cả pipeline tắc. Bài học: luôn định nghĩa interface (Pydantic model) trước khi từng người bắt đầu code.

## 6. Nếu làm lại
Sẽ yêu cầu mỗi thành viên viết một unit test nhỏ cho module của mình ngay ngày đầu — chạy với mock data cứng, không cần gọi API. Việc này phát hiện lỗi interface sớm hơn 4-6 tiếng so với thực tế: nhóm phát hiện mismatch schema giữa `rank_candidates` và `deep_agent.analyze` khá muộn vì không ai test end-to-end sớm.

## 7. AI giúp gì / AI sai gì
- **Giúp:** Dùng Claude để brainstorm kiến trúc pipeline — nó gợi ý thêm tầng "cache kết quả phân tích CV" để không phải gọi lại LLM khi re-rank. Nhóm chưa implement nhưng đây là ý tưởng đúng hướng cho production.
- **Sai/mislead:** Claude gợi ý dùng `asyncio` để chạy batch CV analysis song song ngay từ đầu — nghe hấp dẫn nhưng với hackathon 1 ngày, debug async + API rate limit phức tạp hơn nhiều so với sequential. Suýt mất 2-3 tiếng nếu không quyết định dừng lại và chọn sequential loop đơn giản.
