from langchain_ollama import OllamaLLM
import os

def init_llm(model="llama3.2:1b"):
    base_url = os.getenv("OLLAMA_URL")
    return OllamaLLM(model=model, base_url=base_url)

