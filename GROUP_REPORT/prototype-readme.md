# Prototype — Smart CV-JD Matching

## Mô tả
Prototype này tự động phân tích JD và hàng loạt CV bằng LLM, sau đó tính điểm matching để xếp hạng ứng viên phù hợp nhất. Với nhóm ứng viên top đầu, hệ thống tiếp tục phân tích sâu điểm mạnh/yếu so với JD và sinh bộ câu hỏi phỏng vấn mục tiêu. Luồng chính đã chạy thật qua giao diện Streamlit: upload JD/CV -> analyze -> ranking -> deep analysis -> interview questions.

## Level: Working prototype (MVP)
- Core pipeline chạy end-to-end trong main.py và cho output thật ở data/final_pipeline_results.json.
- Có giao diện demo bằng Streamlit trong ui/app.py để chạy flow tuyển dụng từ đầu đến cuối.
- Agent-based architecture đã tách rõ các bước: JD Analyzer, CV Analyzer, Deep Analyzer, Interview Question Generator.

## Links
- GitHub repo: https://github.com/fisherman611/NhomB6-401-Day06
- UI app (local demo): streamlit run ui/app.py
- CLI pipeline (local demo): python main.py

## Tools và API đã dùng
- Language/runtime: Python
- UI: Streamlit
- LLM SDK: OpenAI Python SDK (openai)
- LLM Endpoint: NVIDIA-hosted OpenAI-compatible API (qua NVIDIA_API_KEY + NVIDIA_BASE_URL)
- Model đang gọi mặc định: openai/gpt-oss-20b
- Data validation/schema: Pydantic
- Config/env: python-dotenv
- API server dependencies (mở rộng): FastAPI, Uvicorn
- Parsing/input utilities: PyPDF2, python-docx
- Data processing: pandas
- Testing: pytest (thư mục test)

## Phân công
| Thành viên | Phần | Output |
|-----------|------|--------|
| Nguyễn Như Giáp | Team lead, thiết kế kiến trúc tổng thể và điều phối pipeline CLI end-to-end | main.py, cấu trúc thư mục src/, data/final_pipeline_results.json |
| Lương Hữu Thành | Backend LLM integration, xây dựng service gọi NVIDIA NIM qua OpenAI-compatible API và cơ chế fallback | src/engine/llm_service.py, .env.example |
| Vũ Như Đức | CV Analysis Engineer, thiết kế schema + prompt trích xuất CV và xử lý fallback parsing JSON | src/agents/cv_analyzer.py, src/prompts/cv_analysis_pt.txt |
| Nguyễn Tiến Thắng | JD Analysis Engineer + data preparation cho JD, thiết kế schema JD và sinh mock JD | src/agents/jd_analyzer.py, src/models/jd_models.py, src/prompts/jd_analysis_pt.txt, scratch/gen_mock_jds.py |
| Hoàng Văn Bắc | Matching & Ranking Algorithm Engineer, phát triển thuật toán tính điểm và xếp hạng ứng viên | src/utils.py (calculate_matching_score, calculate_matching_score_v2, rank_candidates) |
| Trần Anh Tú | AI Agent Engineer cho deep analysis và sinh câu hỏi phỏng vấn cá nhân hóa | src/agents/candidate_deep_analyzer.py, src/agents/interview_question_generator.py, src/prompts/candidate_deep_analysis_pt.txt, src/prompts/interview_question_generator_pt.txt, data/interview_question_db.json |
| Vũ Phúc Thành | Frontend demo và test engineer, xây dựng UI Streamlit và bộ test batch cho các agent | ui/app.py, test/test_cv_analyzer.py, test/test_jd_analyzer.py, test/test_candidate_deep_analyzer.py, test/test_interview_question_generator.py, data/ |
