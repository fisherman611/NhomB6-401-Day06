import os
import json
from src.engine.llm_service import LLMService

class InterviewQuestionSelector:
    def __init__(self, llm_service: LLMService = None):
        self.llm_service = llm_service or LLMService()
        self.prompt_path = "src/prompts/selection_pt.txt"

    def _load_prompt(self):
        if not os.path.exists(self.prompt_path):
            return "Dựa trên CV của ứng viên và kho câu hỏi, hãy chọn ra 5 câu hỏi phù hợp nhất. \nCV: {cv_analysis} \nQuestions: {question_db}"
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def select_questions(self, cv_analysis: str, question_db_path: str):
        """
        Dựa trên kết quả phân tích CV và Database câu hỏi để chọn ra các câu hỏi phù hợp.
        """
        # 1. Load Question DB
        db_content = ""
        if os.path.exists(question_db_path):
            with open(question_db_path, "r", encoding="utf-8") as f:
                db_content = f.read()
        
        # 2. Prepare Prompt
        template = self._load_prompt()
        prompt = template.format(cv_analysis=cv_analysis, question_db=db_content)
        
        # 3. Call LLM
        response = self.llm_service.get_completion(prompt)
        return response

if __name__ == "__main__":
    selector = InterviewQuestionSelector()
    # print(selector.select_questions("Phân tích CV...", "data/database/questions.json"))
