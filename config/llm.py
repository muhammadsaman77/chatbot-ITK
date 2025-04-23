from llama_index.llms.groq import Groq

def init_llm(model="llama-3.2-1b-preview"):
  api_key="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"
  llm = Groq(model=model, api_key=api_key)
  return llm

llm = init_llm()
response = llm.complete("What is the capital of France?")
llm.e
print(response)