from pydantic import BaseModel, Field
from typing import List

class JDStructuredOutput(BaseModel):
    job_title: str = Field(..., description="Tên vị trí công việc")
    required_skills: List[str] = Field(..., description="Danh sách các kỹ năng bắt buộc")
    preferred_skills: List[str] = Field(..., description="Danh sách các kỹ năng ưu tiên")
    experience_level: str = Field(..., description="Cấp độ kinh nghiệm yêu cầu (ví dụ: Junior, Senior, v.v.)")
    key_responsibilities: List[str] = Field(..., description="Danh sách 3-5 trách nhiệm chính trong công việc")
