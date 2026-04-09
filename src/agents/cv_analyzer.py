import json
import logging
import re
from pathlib import Path
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.engine.llm_service import LLMService

logger = logging.getLogger(__name__)


class CVAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")

    full_name: str = Field(default="")
    years_of_experience: float = Field(default=0)
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    education: str = Field(default="")
    summary: str = Field(default="")

class CVAnalyzer:
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or LLMService()
        self.prompt_path = Path(__file__).resolve().parents[1] / "prompts" / "cv_analysis_pt.txt"

    def _load_prompt(self):
        if not self.prompt_path.exists():
            return "Bạn là một chuyên gia tuyển dụng. Hãy phân tích CV sau: {cv_content}"
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
        Thử lần lượt từng khối ``` ... ``` (tránh greedy một lần bắt nhầm nhiều block).
        """
        if not text:
            raise ValueError("LLM response is empty")

        cleaned = text.strip()

        # Mỗi fence ``` ... ``` thử parse riêng (ưu tiên khối đầu tiên parse được)
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

    def analyze(self, cv_text: str) -> dict[str, Any]:
        """
        Phân tích nội dung CV thô thành dữ liệu cấu trúc (JSON).
        """
        if not cv_text or not cv_text.strip():
            raise ValueError("cv_text must not be empty")

        # 1. Load prompt template
        template = self._load_prompt()
        
        # 2. Format prompt
        prompt = template.format(cv_content=cv_text)
        
        # 3. Ưu tiên structured output để đảm bảo đúng schema.
        try:
            parsed = self.llm_service.get_completion_with_structured_output(
                prompt=prompt,
                response_model=CVAnalysis,
            )
            return CVAnalysis.model_validate(parsed).model_dump()
        except Exception as e:
            logger.warning(
                "Structured CV output failed (%s); using text completion fallback",
                e,
            )

        # 4. Fallback: gọi completion thường rồi tự parse/validate.
        raw_response = self.llm_service.get_completion(prompt)
        parsed_json = self._extract_json_object(raw_response or "")
        validated = CVAnalysis.model_validate(parsed_json)
        return self._model_to_dict(validated)

if __name__ == "__main__":
    # Test shortcut
    analyzer = CVAnalyzer()
    # print(analyzer.analyze("Nội dung CV giả lập..."))
