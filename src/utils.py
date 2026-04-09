import logging
import math
import os
import re
from difflib import SequenceMatcher
from typing import Any, Callable, Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)

_SKILL_SYNONYMS = {
    "ml": "machine learning",
    "machine-learning": "machine learning",
    "ai": "artificial intelligence",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "js": "javascript",
    "ts": "typescript",
    "pytorch/tensorflow": "pytorch tensorflow",
    "tf": "tensorflow",
    "k8s": "kubernetes",
    "db": "database",
}


def _normalize_skill_text(text: Any) -> str:
    if text is None:
        return ""
    normalized = str(text).lower().strip()
    normalized = normalized.replace("&", " and ")
    normalized = normalized.replace("/", " ")
    normalized = re.sub(r"[^a-z0-9\s+.-]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return _SKILL_SYNONYMS.get(normalized, normalized)


def _normalize_skill_list(raw_values: Any) -> List[str]:
    if raw_values is None:
        return []
    if not isinstance(raw_values, list):
        raw_values = [raw_values]

    cleaned = []
    for item in raw_values:
        value = _normalize_skill_text(item)
        if value:
            cleaned.append(value)
    return cleaned


def _tokenize_skill(text: str) -> set:
    return set(token for token in text.split() if token)


def _skill_similarity(skill_a: str, skill_b: str) -> float:
    if not skill_a or not skill_b:
        return 0.0
    if skill_a == skill_b:
        return 1.0

    tokens_a = _tokenize_skill(skill_a)
    tokens_b = _tokenize_skill(skill_b)
    if not tokens_a or not tokens_b:
        return 0.0

    intersection = len(tokens_a.intersection(tokens_b))
    union = len(tokens_a.union(tokens_b))
    jaccard = intersection / union if union else 0.0
    seq_ratio = SequenceMatcher(None, skill_a, skill_b).ratio()

    # Combine both metrics: Jaccard (60%) + SequenceMatcher (40%)
    # Jaccard better for token-level, SequenceMatcher better for typos
    return jaccard * 0.6 + seq_ratio * 0.4


def _coverage_score(jd_skills: Sequence[str], cv_skills: Sequence[str], threshold: float = 0.55) -> float:
    if not jd_skills:
        return 0.0
    if not cv_skills:
        return 0.0

    total_score = 0.0
    for jd_skill in jd_skills:
        best = 0.0
        for cv_skill in cv_skills:
            sim = _skill_similarity(jd_skill, cv_skill)
            if sim > best:
                best = sim
        # Clamp noisy fuzzy matches below threshold
        total_score += best if best >= threshold else 0.0

    return total_score / len(jd_skills)


def _hash_embedding(text: str, dim: int = 256) -> List[float]:
    vector = [0.0] * dim
    for token in re.findall(r"[a-z0-9+#.]+", text.lower()):
        # Use deterministic hash for reproducibility
        idx = sum(ord(c) * (i + 1) for i, c in enumerate(token)) % dim
        vector[idx] += 1.0
    return vector


def _cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    if not vec_a or not vec_b:
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _summary_similarity(cv_summary: str, jd_summary: str) -> float:
    """
    Tính độ tương đồng giữa 2 summary bằng hash embedding (không dùng API).
    Sử dụng cosine similarity trên vector hash cơ bản.
    """
    if not cv_summary or not jd_summary:
        return 0.0
    
    cv_vec = _hash_embedding(cv_summary, dim=256)
    jd_vec = _hash_embedding(jd_summary, dim=256)
    return _cosine_similarity(cv_vec, jd_vec)


def _embedding_similarity(
    cv_text: str,
    jd_text: str,
    embedding_fn: Optional[Callable[[str], Sequence[float]]] = None,
    embedding_model: str = "text-embedding-3-small",
) -> float:
    """Compute embedding similarity using local hash vectorizer (no API calls)."""
    try:
        if embedding_fn is not None:
            cv_vec = embedding_fn(cv_text)
            jd_vec = embedding_fn(jd_text)
            return max(0.0, min(1.0, _cosine_similarity(cv_vec, jd_vec)))
    except Exception as embedding_error:
        logger.warning("Custom embedding function failed, using local hash vectorizer: %s", embedding_error)

    # Default: use local hash embedding (no API calls)
    cv_vec = _hash_embedding(cv_text)
    jd_vec = _hash_embedding(jd_text)
    return max(0.0, min(1.0, _cosine_similarity(cv_vec, jd_vec)))

def calculate_matching_score(cv_data: Dict[str, Any], jd_data: Dict[str, Any]) -> float:
    """
    Tính toán điểm matching giữa CV và JD dựa trên từ khóa (Keywords Matching).
    
    Logic:
    - So khớp kỹ năng kỹ thuật (Technical Skills).
    - So khớp kỹ năng mềm (Soft Skills) - nếu JD có đề cập.
    - Điểm cộng cho Preferred Skills.
    """
    try:
        cv_tech_skills = set(s.lower().strip() for s in cv_data.get("technical_skills", []))
        jd_req_skills = set(s.lower().strip() for s in jd_data.get("required_skills", []))
        jd_pref_skills = set(s.lower().strip() for s in jd_data.get("preferred_skills", []))
        
        if not jd_req_skills:
            return 0.0
            
        # 1. Điểm kỹ năng bắt buộc (Trọng số 70%)
        matches_req = cv_tech_skills.intersection(jd_req_skills)
        score_req = len(matches_req) / len(jd_req_skills) if jd_req_skills else 0
        
        # 2. Điểm kỹ năng ưu tiên (Trọng số 30%)
        # Nếu không có kỹ năng ưu tiên trong JD, ta coi như ứng viên đạt tối đa phần này nếu có skill bắt buộc tốt
        if jd_pref_skills:
            matches_pref = cv_tech_skills.intersection(jd_pref_skills)
            score_pref = len(matches_pref) / len(jd_pref_skills)
        else:
            score_pref = score_req # Fallback
            
        final_score = (score_req * 0.7) + (score_pref * 0.3)
        
        # Làm tròn 2 chữ số thập phân
        return round(final_score * 100, 2)
        
    except Exception as e:
        logger.error(f"Lỗi khi tính điểm matching: {e}")
        return 0.0


def calculate_matching_score_v2(
    cv_data: Dict[str, Any],
    jd_data: Dict[str, Any],
) -> float:
    """
    Matching score version 2:
    - Keyword matching robust hơn: normalize/synonym/fuzzy coverage.
    - Semantic score dựa trên so sánh summary (hash embedding, không gọi API).
    - Trọng số động dựa trên dữ liệu có sẵn.
    
    Thành phần:
    1. Required skills (70%): Kỹ năng bắt buộc
    2. Preferred skills (20%): Kỹ năng ưu tiên
    3. Summary embedding (10%): Độ tương đồng ngữ cảnh qua summary
    """
    try:
        # Extract và normalize skills từ CV
        cv_tech_skills = _normalize_skill_list(cv_data.get("technical_skills", []))
        cv_summary = str(cv_data.get("summary", "")).strip()

        # Extract và normalize từ JD
        jd_req_skills = _normalize_skill_list(jd_data.get("required_skills", []))
        jd_pref_skills = _normalize_skill_list(jd_data.get("preferred_skills", []))
        jd_summary = str(jd_data.get("summary", "")).strip()

        # 1) Keyword coverage cho required skills
        score_req = _coverage_score(jd_req_skills, cv_tech_skills) if jd_req_skills else 0.0
        
        # 2) Keyword coverage cho preferred skills
        score_pref = _coverage_score(jd_pref_skills, cv_tech_skills) if jd_pref_skills else 0.0

        # 3) Summary embedding similarity (local hash embedding, no API cost)
        score_semantic = _summary_similarity(cv_summary, jd_summary) if cv_summary and jd_summary else 0.0

        # 4) Dynamic weighted blending
        # Trọng số: req 70%, pref 20%, semantic 10%
        components = {
            "req": (score_req, 0.7, bool(jd_req_skills)),
            "pref": (score_pref, 0.2, bool(jd_pref_skills)),
            "semantic": (score_semantic, 0.1, bool(cv_summary) and bool(jd_summary)),
        }

        # Chỉ tính trọng số cho các thành phần có dữ liệu
        active = {k: v for k, v in components.items() if v[2]}
        if not active:
            return 0.0

        total_weight = sum(v[1] for v in active.values())
        blended_score = sum((score * weight) for score, weight, _ in active.values()) / total_weight

        return round(max(0.0, min(1.0, blended_score)) * 100, 2)

    except Exception as e:
        logger.error(f"Lỗi khi tính điểm matching v2: {e}")
        return 0.0


def rank_candidates(candidates: List[Dict[str, Any]], jd_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Xếp hạng danh sách ứng viên dựa trên điểm matching với JD.
    Đầu vào: 
    - candidates: Danh sách dict, mỗi dict chứa cv_analysis và thông tin ứng viên.
    - jd_data: Kết quả phân tích JD.
    """
    ranked_list = []
    
    for candidate in candidates:
        cv_analysis = candidate.get("cv_analysis", {})
        score = calculate_matching_score_v2(cv_analysis, jd_data)
        
        # Gắn thêm điểm số vào object ứng viên
        candidate_with_score = candidate.copy()
        candidate_with_score["matching_score"] = score
        ranked_list.append(candidate_with_score)
        
    # Sắp xếp giảm dần theo điểm số
    ranked_list.sort(key=lambda x: x["matching_score"], reverse=True)
    
    return ranked_list

if __name__ == "__main__":
    # Test nhanh logic matching
    mock_cv = {
  "full_name": "Le Thao Nguyen",
  "years_of_experience": 5.0,
  "technical_skills": [
    "Manual Testing",
    "Test Case Design",
    "Jira",
    "Postman",
    "SQL"
  ],
  "soft_skills": [
    "Can than",
    "Giao tiep noi bo",
    "Lam viec theo quy trinh",
    "Quan ly deadline"
  ],
  "education": "Cử nhân Hệ thống thông tin",
  "summary": "Ứng viên có 5 năm kinh nghiệm trong lĩnh vực kiểm thử phần mềm, chuyên làm QA Engineer và Tester. Hiện chưa có kinh nghiệm giảng dạy hoặc làm việc trong lĩnh vực trí tuệ nhân tạo. Không đáp ứng đầy đủ yêu cầu Senior AI Instructor."
}

    mock_jd = {
  "job_title": "Giảng viên Cao cấp Trí tuệ Nhân tạo (Senior AI Instructor)",
  "years_of_experience": 5.0,
  "technical_skills": [
    "Python",
    "PyTorch",
    "TensorFlow",
    "CNN",
    "RNN",
    "Transformers",
    "Deep Learning",
    "Reinforcement Learning",
    "Computer Vision"
  ],
  "soft_skills": [
    "Kỹ năng sư phạm tốt",
    "Khả năng truyền cảm hứng",
    "Khả năng đọc hiểu tài liệu tiếng Anh chuyên ngành tốt",
    "Kỹ năng tư vấn"
  ],
  "education": "Tiến sĩ chuyên ngành AI, Computer Science hoặc các lĩnh vực liên quan",
  "summary": "Giảng viên cao cấp sẽ thiết kế và giảng dạy các chương trình đào tạo chuyên sâu về AI, Deep Learning và Reinforcement Learning, hướng dẫn sinh viên thực hiện dự án nghiên cứu trong lĩnh vực thị giác máy tính. Ngoài ra, họ sẽ cập nhật giáo trình, tham gia nghiên cứu khoa học, công bố bài báo quốc tế và tư vấn cho các nhóm khởi nghiệp công nghệ."
}
    
    score = calculate_matching_score_v2(mock_cv, mock_jd)
    print(f"Test Matching Score: {score}%")
