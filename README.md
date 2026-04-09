# Smart CV-JD Matching

Hệ thống AI hỗ trợ tuyển dụng theo hướng augmentation: tự động phân tích JD và CV, chấm điểm matching, xếp hạng ứng viên, phân tích sâu điểm mạnh/yếu và sinh câu hỏi phỏng vấn phù hợp.

## 1. Mục tiêu dự án

- Giảm thời gian screening CV cho HR.
- Tăng độ nhất quán trong việc đánh giá ứng viên theo JD.
- Hỗ trợ chuẩn bị bộ câu hỏi phỏng vấn có định hướng theo từng ứng viên.

## 2. Tính năng chính

- Phân tích JD thành dữ liệu cấu trúc (job title, required/preferred skills, summary...).
- Phân tích CV thành dữ liệu cấu trúc (họ tên, kinh nghiệm, technical skills, summary...).
- Tính điểm matching theo thuật toán kết hợp keyword + fuzzy + semantic summary.
- Xếp hạng ứng viên và chọn Top-N.
- Deep analysis cho Top-N để tìm strengths/weaknesses so với JD.
- Sinh bộ câu hỏi phỏng vấn dựa trên deep analysis và database nội bộ.
- Demo UI bằng Streamlit và pipeline CLI end-to-end.

## 3. Kiến trúc tổng quan

Pipeline gồm 5 bước:

1. Analyze JD
2. Analyze batch CV
3. Matching + Ranking
4. Deep Analysis cho Top-N
5. Interview Question Generation

Thành phần chính:

- LLM service: [src/engine/llm_service.py](src/engine/llm_service.py)
- CV analyzer: [src/agents/cv_analyzer.py](src/agents/cv_analyzer.py)
- JD analyzer: [src/agents/jd_analyzer.py](src/agents/jd_analyzer.py)
- Deep analyzer: [src/agents/candidate_deep_analyzer.py](src/agents/candidate_deep_analyzer.py)
- Interview question generator: [src/agents/interview_question_generator.py](src/agents/interview_question_generator.py)
- Matching utility: [src/utils.py](src/utils.py)
- CLI pipeline: [main.py](main.py)
- Streamlit UI: [ui/app.py](ui/app.py)

## 4. Cấu trúc thư mục quan trọng


- Dữ liệu đầu vào CV: [data/data_cv](data/data_cv)
- Dữ liệu đầu vào JD: [data/data_jd](data/data_jd)
- Kết quả pipeline tổng: [data/final_pipeline_results.json](data/final_pipeline_results.json)
- Kết quả test theo từng bước:
	- [data/cv_analysis_results](data/cv_analysis_results)
	- [data/jd_analysis_results](data/jd_analysis_results)
	- [data/deep_analysis_results](data/deep_analysis_results)
	- [data/interview_questions](data/interview_questions)
- DB câu hỏi phỏng vấn: [data/interview_question_db.json](data/interview_question_db.json)

## 5. Yêu cầu môi trường

- Python 3.10+ (khuyến nghị 3.11)
- API key cho NVIDIA OpenAI-compatible endpoint

## 6. Cài đặt nhanh

```bash
git clone https://github.com/fisherman611/NhomB6-401-Day06.git
cd NhomB6-401-Day06
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 7. Cấu hình biến môi trường

1. Tạo file .env từ mẫu [.env.example](.env.example)
2. Điền giá trị thực tế:

```env
NVIDIA_API_KEY=your_key
NVIDIA_BASE_URL=your_base_url
DATABASE_PATH=data/interview_question_db.json
TOP_N=3
```

Lưu ý: Pipeline hiện tại đọc trực tiếp tham số trong code và UI; DATABASE_PATH/TOP_N trong .env có thể được dùng để mở rộng về sau.

## 8. Chạy ứng dụng

### 8.1 Chạy pipeline CLI

```bash
python main.py
```

Kết quả tổng hợp được lưu tại [data/final_pipeline_results.json](data/final_pipeline_results.json).

### 8.2 Chạy giao diện Streamlit

```bash
streamlit run ui/app.py
```

Flow trên UI:

1. Upload 1 file JD (.txt)
2. Upload nhiều file CV (.txt)
3. Chọn Top-N ở sidebar
4. Nhấn nút chạy pipeline
5. Xem ranking, deep analysis và interview questions

## 9. Chạy test theo từng module

Dự án hiện có các test script batch (không phải full unit test suite). Chạy từ thư mục gốc dự án.

### CV Analyzer

```bash
python test/test_cv_analyzer.py \
	--input-dir data/data_cv \
	--output-dir data/cv_analysis_results
```

### JD Analyzer

```bash
python test/test_jd_analyzer.py \
	--input-dir data/data_jd \
	--output-dir data/jd_analysis_results
```

### Candidate Deep Analyzer

```bash
python test/test_candidate_deep_analyzer.py \
	--cv-dir data/cv_analysis_results \
	--jd-file data/jd_analysis_results/jd_ai_01.json \
	--output-dir data/deep_analysis_results
```

### Interview Question Generator

```bash
python test/test_interview_question_generator.py \
	--input-dir data/deep_analysis_results \
	--output-dir data/interview_questions \
	--db-path data/interview_question_db.json \
	--pos "Giang vien Tri tue Nhan tao"
```

## 10. Công nghệ sử dụng

- Python
- OpenAI Python SDK (gọi NVIDIA OpenAI-compatible endpoint)
- Pydantic
- Streamlit
- python-dotenv
- pandas

## 11. Hạn chế hiện tại

- Chưa có bộ metric đánh giá chất lượng matching/deep analysis có ground truth.
- Chưa có feedback loop từ thao tác HR để tự động cải tiến scoring.
- Error handling batch trên UI có thể cải tiến thêm để skip từng CV lỗi thay vì dừng toàn bộ process.

## 12. Tài liệu liên quan

- Prototype summary + phân công: [GROUP_REPORT/prototype-readme.md](GROUP_REPORT/prototype-readme.md)
- SPEC hackathon: [GROUP_REPORT/SPEC_final.md](GROUP_REPORT/SPEC_final.md)

## 13. Team

- Nguyễn Như Giáp
- Lương Hữu Thành
- Vũ Như Đức
- Nguyễn Tiến Thắng
- Hoàng Văn Bắc
- Trần Anh Tú
- Vũ Phúc Thành