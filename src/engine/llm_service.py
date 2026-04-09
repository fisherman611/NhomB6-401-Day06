import os
import json
from typing import Type, TypeVar
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")
base_url = os.getenv("NVIDIA_BASE_URL")

class LLMService:
    def __init__(self, temperature: float = 0, top_p: float = 0.7):
        self.api_key = api_key
        self.base_url = base_url
        self.temperature = temperature
        self.top_p = top_p
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def get_completion(self, prompt, model="openai/gpt-oss-20b"):
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=self.temperature,
            top_p=self.top_p,
        )
        return response.choices[0].message.content

    def get_completion_with_structured_output(self, prompt: str, response_model: Type[BaseModel], model="openai/gpt-oss-20b"):
        messages = [{"role": "user", "content": prompt}]
        
        try:
            # Try using the beta parse method for better Pydantic integration
            response = self.client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                response_format=response_model,
                temperature=self.temperature,
                top_p=self.top_p,
            )
            return response.choices[0].message.parsed
        except Exception as e:
            # Fallback for models/endpoints that don't support beta.chat.completions.parse
            # Force JSON mode if possible or just parse the text
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=self.temperature,
                top_p=self.top_p,
            )
            content = response.choices[0].message.content
            return response_model.model_validate_json(content)

if __name__ == "__main__":
    llm_service = LLMService()
    print(llm_service.get_completion("Hello"))
