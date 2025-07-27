from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def init_embedding(model_name="firqaaa/indo-sentence-bert-base"):
  embed_model = HuggingFaceEmbedding(
    model_name=model_name,
  )
  return embed_model
  