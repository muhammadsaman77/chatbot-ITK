import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

def init_chroma():
  db = chromadb.PersistentClient(path="./chroma")
  chroma_collection = db.get_or_create_collection(name="chatbot_informasi_ITK")
  vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
  return vector_store