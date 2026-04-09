import os
import sys
from pathlib import Path

# Thêm project root vào sys.path để tránh lỗi ModuleNotFoundError khi chạy trực tiếp
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import logging
import re
from pathlib import Path
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.engine.llm_service import LLMService

logger = logging.getLogger(__name__)


class JDAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")

    job_title: str = Field(default="")
    years_of_experience: float = Field(default=0)
    required_skills: List[str] = Field(default_factory=list, description="Kỹ năng bắt buộc")
    preferred_skills: List[str] = Field(default_factory=list, description="Kỹ năng ưu tiên")
    soft_skills: List[str] = Field(default_factory=list)
    education: str = Field(default="")
    summary: str = Field(default="")

class JDAnalyzer:
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
        self.prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "jd_analysis_pt.txt"

    def _load_prompt(self):
        if not self.prompt_path.exists():
            return "Hãy phân tích bản mô tả công việc (JD) sau và trích xuất các yêu cầu chính: {jd_content}"
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _try_parse_json_object(self, fragment: str) -> Optional[dict[str, Any]]:
        fragment = fragment.strip()
        if not fragment:
            return None
        try:
            out = json.loads(fragment)
            if isinstance(out, dict):
                return out
        except json.JSONDecodeError:
            pass
        start = fragment.find("{")
        end = fragment.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                out = json.loads(fragment[start : end + 1])
                if isinstance(out, dict):
                    return out
            except json.JSONDecodeError:
                pass
        return None

    def _extract_json_object(self, text: str) -> dict[str, Any]:
        """
        Cố gắng bóc tách JSON object từ response text (kể cả khi bị bọc markdown).
        """
        if not text:
            raise ValueError("LLM response is empty")

        cleaned = text.strip()

        # Mỗi fence ``` ... ``` thử parse riêng
        for m in re.finditer(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned):
            block = m.group(1)
            parsed = self._try_parse_json_object(block)
            if parsed is not None:
                return parsed

        parsed = self._try_parse_json_object(cleaned)
        if parsed is not None:
            return parsed

        raise ValueError("Could not parse JSON object from LLM response")

    def _model_to_dict(self, model_obj: BaseModel) -> dict[str, Any]:
        if hasattr(model_obj, "model_dump"):
            return model_obj.model_dump()
        return model_obj.dict()

    def analyze(self, jd_text: str) -> dict[str, Any]:
        """
        Phân tích JD thô để lấy ra các yêu cầu về kỹ năng, kinh nghiệm.
        """
        if not jd_text or not jd_text.strip():
            raise ValueError("jd_text must not be empty")

        # 1. Load prompt template
        template = self._load_prompt()
        
        # 2. Format prompt
        prompt = template.format(jd_content=jd_text)
        
        # 3. Ưu tiên structured output
        try:
            parsed = self.llm_service.get_completion_with_structured_output(
                prompt=prompt,
                response_model=JDAnalysis,
            )
            return JDAnalysis.model_validate(parsed).model_dump()
        except Exception as e:
            logger.warning(
                "Structured JD output failed (%s); using text completion fallback",
                e,
            )

        # 4. Fallback: gọi completion thường
        raw_response = self.llm_service.get_completion(prompt)
        parsed_json = self._extract_json_object(raw_response or "")
        validated = JDAnalysis.model_validate(parsed_json)
        return self._model_to_dict(validated)

if __name__ == "__main__":
    # Test shortcut
    analyzer = JDAnalyzer()
    print(analyzer.analyze("Nội dung JD giả lập..."))
