# Individual Reflection — Hoàng Văn Bắc

## 1. Role
Matching & Ranking Algorithm Engineer. Phụ trách toàn bộ logic tính điểm tương đồng giữa CV và JD — component cốt lõi quyết định ứng viên nào được chọn vào Top-N.

## 2. Đóng góp cụ thể
- Viết `calculate_matching_score()` (v1) trong `src/utils.py` — keyword matching đơn giản: so khớp exact string giữa `cv.technical_skills` vs `jd.required_skills` (trọng số 70%) và `jd.preferred_skills` (30%), trả về điểm 0-100.
- Viết `calculate_matching_score_v2()` — thuật toán matching nâng cao gồm 3 thành phần: (1) fuzzy coverage score cho required skills (kết hợp Jaccard similarity và SequenceMatcher ratio, threshold 0.55), (2) fuzzy coverage cho preferred skills, (3) semantic summary similarity qua hash embedding + cosine similarity (không gọi API). Implement normalize/synonym mapping (`_SKILL_SYNONYMS`) để xử lý "ML" → "machine learning", "k8s" → "kubernetes".
- Viết `rank_candidates()` — nhận danh sách candidates, tính điểm matching cho từng người bằng `calculate_matching_score()`, sort giảm dần và trả về ranked list — hàm này được `main.py` và `ui/app.py` sử dụng trực tiếp.

## 3. SPEC mạnh/yếu
- **Mạnh nhất: Algorithm design với failure modes** — `calculate_matching_score_v2()` có dynamic weight blending: nếu JD không có `preferred_skills` thì weight tự điều chỉnh, nếu không có summary thì bỏ semantic component — tránh điểm 0 do thiếu dữ liệu, giải quyết tốt edge case JD không đầy đủ thông tin.
- **Yếu nhất: Evaluation với ground truth** — không có labeled dataset để đo xem v2 có thực sự tốt hơn v1 không. Chỉ test thủ công với mock CV/JD trong `__main__` block của `utils.py`. Không biết fuzzy threshold `0.55` là tối ưu hay chỉ là con số "nghe có vẻ hợp lý".

## 4. Đóng góp khác
- Test và validate `calculate_matching_score_v2()` với bộ mock data có sẵn trong `__main__` block — ứng viên QA Engineer với JD Senior AI Instructor cho điểm thấp đúng như mong đợi (~15%), xác nhận logic hoạt động đúng hướng.
- Phát hiện và báo cáo lỗi: `rank_candidates()` gọi `calculate_matching_score()` (v1) trong khi UI (`app.py`) gọi `calculate_matching_score_v2()` trực tiếp — hai bước pipeline dùng scoring algorithm khác nhau. Cần thống nhất hoặc để người dùng chọn version.

## 5. Điều học được
Trước hackathon nghĩ fuzzy matching chỉ là "so sánh chuỗi nâng cao". Qua việc implement `_skill_similarity()` mới hiểu: kết hợp Jaccard (token overlap) và SequenceMatcher (character-level) cho kết quả tốt hơn từng method riêng lẻ vì chúng bổ sung cho nhau — Jaccard tốt với từ rời ("deep learning" vs "deep-learning"), SequenceMatcher tốt với typo ("pytorch" vs "Pytorch"). Đây là bài học về ensemble methods áp dụng ở cấp độ string matching.

## 6. Nếu làm lại
Sẽ tạo một bộ 20 cặp CV-JD được label thủ công (ground truth: "ứng viên này nên được chọn") từ ngày đầu, dùng bộ này để measure precision/recall của cả v1 và v2 trước khi chọn algorithm cho pipeline. Hiện tại không có cơ sở để biết v2 thực sự tốt hơn v1 bao nhiêu % trong thực tế.

## 7. AI giúp gì / AI sai gì
- **Giúp:** Dùng Claude để brainstorm các kỹ thuật normalize skill text — Claude gợi ý synonym mapping dict (`_SKILL_SYNONYMS`) là cách đơn giản nhất để handle các alias phổ biến mà không cần model embedding riêng. Implement được trong 30 phút.
- **Sai/mislead:** Claude gợi ý dùng `sentence-transformers` để tính semantic similarity thay vì hash embedding — về chất lượng thì đúng, nhưng `sentence-transformers` cần download model (vài trăm MB) và không chắc có internet trong demo environment. Hash embedding tuy kém hơn nhưng zero-dependency và instant. AI không cân nhắc constraint deployment khi đưa ra gợi ý.
