from langchain_chroma import Chroma
from .embedding import init_embedding

def init_chroma():
  embeding_function = init_embedding()
  vector_store = Chroma(
    collection_name="chatbot_informasi_ITK",
    embedding_function=embeding_function,
    persist_directory="./chroma_langchain_db",
)

  return vector_store
