from langchain_core.language_models import LLM
from langchain_core.prompts import PromptTemplate
import requests
from typing import List, Optional
from dotenv import load_dotenv
import os

load_dotenv(override=True)
config = os.environ


API_URL = config.get("API_URL")
MODEL_NAME = config.get("MODEL_NAME")
API_KEY = config.get("API_KEY")

class CustomLLM(LLM):
    model: str
    endpoint_url: str = API_URL
    headers: dict = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY
    }
    temperature: float = 0.7
    top_p: float = 1.0
    max_tokens: int = 2000
    stream: bool = False
    stop: Optional[List[str]] = None

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens
        }
        if stop:
            payload["stop"] = stop
        response = requests.post(self.endpoint_url, headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']

    @property
    def _llm_type(self) -> str:
        return "custom-llm"

llm = CustomLLM(
    model=MODEL_NAME,
    temperature=0.5,
    top_p=0.9,
    max_tokens=1000
)

prompt = PromptTemplate.from_template("You are helpful AI. Reply to: {text}")

if __name__ == "__main__":

    API_URL = config.get("API_URL")
    MODEL_NAME = config.get("MODEL_NAME")
    API_KEY = config.get("API_KEY")
    print(API_URL + "\n" + MODEL_NAME + "\n" + API_KEY)

    user_input = prompt.format(text="What is Quantum Computing?")
    response = llm.invoke(user_input)
    print("LLM Response:", response)