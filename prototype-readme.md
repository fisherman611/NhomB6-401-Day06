# Prototype — Smart CV-JD Matching

## Mô tả
Prototype này tự động phân tích JD và hàng loạt CV bằng LLM, sau đó tính điểm matching để xếp hạng ứng viên phù hợp nhất. Với nhóm ứng viên top đầu, hệ thống tiếp tục phân tích sâu điểm mạnh/yếu so với JD và sinh bộ câu hỏi phỏng vấn mục tiêu. Luồng chính đã chạy thật qua giao diện Streamlit: upload JD/CV -> analyze -> ranking -> deep analysis -> interview questions.

## Level: Working prototype (MVP)
- Core pipeline chạy end-to-end trong main.py và cho output thật ở data/final_pipeline_results.json.
- Có giao diện demo bằng Streamlit trong ui/app.py để chạy flow tuyển dụng từ đầu đến cuối.
- Agent-based architecture đã tách rõ các bước: JD Analyzer, CV Analyzer, Deep Analyzer, Interview Question Generator.

## Links
- GitHub repo: https://github.com/fisherman611/smart_cv_jd_matching
- UI app (local demo): streamlit run ui/app.py
- CLI pipeline (local demo): python main.py
- Video demo (nếu có): [Điền link Drive/YouTube]
- Figma (nếu có): [Điền link Figma]

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
| [Tên 1] | Thiết kế data + prompt cho JD/CV | data/data_jd/, data/data_cv/, src/prompts/ |
| [Tên 2] | Core AI pipeline (agents + scoring) | src/agents/, src/engine/llm_service.py, src/utils.py |
| [Tên 3] | UI demo + tích hợp flow end-to-end | ui/app.py, main.py |
| [Tên 4] | Kiểm thử + đánh giá + tài liệu | test/, README.md, prototype-readme.md |

Gợi ý: thay [Tên 1..4] bằng tên thành viên thực tế của nhóm để nộp bản cuối.
