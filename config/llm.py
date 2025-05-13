from langchain_ollama import OllamaLLM

def init_llm(model="llama3.2:1b"):
  return OllamaLLM(model=model,base_url="http://localhost:11434", )
