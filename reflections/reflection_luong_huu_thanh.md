# Individual Reflection — Lương Hữu Thành

## 1. Role
Backend Engineer phụ trách LLM Integration. Xây dựng lớp kết nối với mô hình ngôn ngữ lớn — trái tim kỹ thuật mà toàn bộ 4 agents trong project phụ thuộc vào.

## 2. Đóng góp cụ thể
- Viết `src/engine/llm_service.py` — class `LLMService` kết nối NVIDIA NIM API qua OpenAI-compatible client, bao gồm hai phương thức: `get_completion()` (text output) và `get_completion_with_structured_output()` (Pydantic model output) với model mặc định `openai/gpt-oss-20b`.
- Implement cơ chế fallback 3 tầng trong `get_completion_with_structured_output()`: (1) thử `beta.chat.completions.parse` cho Pydantic integration tốt nhất, (2) nếu thất bại thì fallback sang `response_format={"type": "json_object"}`, (3) toàn bộ agent cũng có fallback text completion riêng — đảm bảo pipeline không bị crash khi endpoint không hỗ trợ tính năng mới.
- Tạo `.env.example` với hai biến cấu hình `NVIDIA_API_KEY` và `NVIDIA_BASE_URL`, giúp các thành viên khác setup môi trường trong vài phút.

## 3. SPEC mạnh/yếu
- **Mạnh nhất: Failure modes** — thiết kế fallback 3 tầng thực sự phát huy tác dụng khi NVIDIA endpoint không hỗ trợ `beta.parse`. Nhóm không bị mất thời gian debug API incompatibility vì đã có safety net. Đây là quyết định kỹ thuật quan trọng nhất của hackathon.
- **Yếu nhất: Observability** — `LLMService` không có logging về latency, token usage hay retry count. Trong demo, không biết mỗi API call mất bao lâu và tốn bao nhiêu token. Nếu có log này sẽ dễ tối ưu hơn nhiều.

## 4. Đóng góp khác
- Test kết nối API trực tiếp qua `if __name__ == "__main__"` trong `llm_service.py` — gọi `get_completion("Hello")` để xác nhận NVIDIA_API_KEY hợp lệ trước khi các thành viên khác bắt đầu test agent của mình.
- Hỗ trợ Vũ Như Đức và Nguyễn Tiến Thắng debug lỗi `json.JSONDecodeError` khi LLM trả về response bọc trong markdown fence — dẫn đến pattern `_extract_json_object()` với regex được chuẩn hóa và tái sử dụng ở cả 4 agent files.

## 5. Điều học được
Trước hackathon chưa biết NVIDIA NIM có API endpoint tương thích OpenAI. Sau khi tích hợp mới hiểu: khả năng "drop-in replacement" này cho phép dùng lại toàn bộ OpenAI SDK mà chỉ cần thay `base_url` và `api_key` — cực kỳ tiết kiệm thời gian so với tích hợp SDK riêng. Đây là kiến thức thực tế về LLM deployment mà không học được từ sách.

## 6. Nếu làm lại
Sẽ thêm `temperature` và `top_p` vào từng lần gọi như tham số độc lập thay vì chỉ set ở constructor — vì trong hackathon, agent sinh câu hỏi phỏng vấn cần `temperature=0.7` để đa dạng hơn, còn agent phân tích CV cần `temperature=0.1` để nhất quán. Hiện tại cả pipeline dùng chung một instance LLMService với `temperature=0.1` nên câu hỏi phỏng vấn hơi cứng nhắc.

## 7. AI giúp gì / AI sai gì
- **Giúp:** Dùng GitHub Copilot để generate boilerplate cho `get_completion_with_structured_output()` — tiết kiệm ~20 phút viết tay. Copilot đề xuất đúng pattern try/except với fallback.
- **Sai/mislead:** ChatGPT gợi ý dùng `instructor` library để handle structured output — đúng về mặt kỹ thuật nhưng thêm một dependency mới vào `requirements.txt`, cần thời gian test tương thích. Quyết định đúng là dùng native OpenAI SDK fallback thay vì phụ thuộc thêm thư viện bên ngoài trong hackathon.
