from langchain_huggingface import HuggingFaceEmbeddings
def init_embedding(model_name="firqaaa/indo-sentence-bert-base"):
  embed_model = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs={"device": "cuda"}
  )
  return embed_model
  