# Individual Reflection — Vũ Phúc Thành

## 1. Role
Frontend Developer kiêm Test Engineer. Phụ trách xây dựng giao diện Streamlit cho demo (`ui/app.py`), viết bộ test scripts cho toàn bộ agents, và tạo dữ liệu mock phục vụ test của cả nhóm.

## 2. Đóng góp cụ thể
- Viết `ui/app.py` — Streamlit app đầy đủ tính năng: upload JD và nhiều CV qua file uploader, real-time log streaming với custom CSS dark theme (màu terminal-style), progress bar xử lý batch CV, hiển thị kết quả chia 2 tabs ("Elite Candidates" với deep insight và interview questions có thể expand, "Comprehensive Ranking" dạng table), metric summary (số candidates, highest score, deep analysis count).
- Viết 4 test scripts trong `test/`: `test_cv_analyzer.py`, `test_jd_analyzer.py`, `test_candidate_deep_analyzer.py`, `test_interview_question_generator.py` — mỗi file là batch test runner với `argparse` (input-dir, output-dir, pattern), chạy agent trên toàn bộ file trong thư mục và lưu JSON kết quả, in SUMMARY với số lượng success/fail — công cụ này giúp cả nhóm validate từng agent độc lập.
- Tạo `scratch/gen_mock_jds.py` sinh 10 JD files (.txt) phủ 3 domain (AI: 3 JD, CS: 4 JD, Math: 3 JD) với các cấp độ Junior/Middle/Senior đa dạng — bộ data này là nền tảng để toàn nhóm test mà không cần tự viết JD thủ công.

## 3. SPEC mạnh/yếu
- **Mạnh nhất: User experience cho demo** — log streaming với màu sắc theo loại (info=xanh, success=xanh lá, warn=vàng, error=đỏ) và hiệu ứng cursor nhấp nháy tạo cảm giác "hệ thống đang chạy thực sự". Kết hợp với layout 2 cột upload + 2 tabs kết quả, demo trông chuyên nghiệp hơn mức hackathon thông thường.
- **Yếu nhất: Error handling trong UI** — block `except` ở cuối chỉ hiển thị `FATAL ERROR` và dừng lại, không có cơ chế retry hay skip file CV lỗi. Nếu một CV file bị lỗi encoding hoặc LLM timeout, toàn bộ processing dừng lại và người dùng phải upload lại từ đầu. Lẽ ra nên xử lý per-file exception.

## 4. Đóng góp khác
- Phát hiện bug trong UI: `cv_file.read()` chỉ đọc được một lần — nếu user trigger processing lần hai (nhấn nút lại), file objects đã exhausted và trả về empty bytes. Đây là Streamlit gotcha về file uploader state — đã fix bằng cách đọc và cache content vào session state ngay khi file được upload.
- Setup cấu trúc thư mục `data/` hoàn chỉnh: `data_cv/`, `data_jd/`, `cv_analysis_results/`, `jd_analysis_results/`, `deep_analysis_results/`, `interview_questions/` — đảm bảo các test scripts và `main.py` có đúng path để đọc/ghi.

## 5. Điều học được
Trước hackathon chưa biết Streamlit có thể build được UI có cảm giác "live terminal" chỉ bằng `st.markdown()` với custom CSS và `st.empty()` placeholder. Học được kỹ thuật real-time update: thay vì dùng `st.write()` tạo nhiều element mới, dùng một `placeholder = st.empty()` duy nhất và update HTML của nó sau mỗi bước xử lý — tạo hiệu ứng log streaming không cần WebSocket.

## 6. Nếu làm lại
Sẽ thêm per-file error handling vào processing loop trong UI ngay từ đầu: thay vì `raise` exception ngay khi một CV lỗi, sẽ `continue` và log error cho CV đó rồi tiếp tục xử lý các CV còn lại. Đây là UX cơ bản nhất cho batch processing nhưng bị bỏ qua vì tập trung vào happy path trong hackathon.

## 7. AI giúp gì / AI sai gì
- **Giúp:** Dùng Claude để generate CSS cho dark theme terminal-style — Claude produce đúng CSS với gradient button, box-shadow cho card, và keyframe animation cho cursor blink chỉ trong một lần prompt. Tiết kiệm ~45 phút viết CSS thủ công và tự test màu sắc.
- **Sai/mislead:** Claude gợi ý dùng `st.experimental_rerun()` (deprecated API) thay vì `st.rerun()` — nếu follow theo sẽ gặp `AttributeError` với phiên bản Streamlit mới. Bài học: luôn kiểm tra version compatibility khi AI generate code liên quan đến third-party library, đặc biệt với Streamlit vốn thay đổi API thường xuyên.
