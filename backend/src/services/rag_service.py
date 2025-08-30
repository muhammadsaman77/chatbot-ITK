from datetime import timedelta
import os
from uuid import uuid4
from langchain_chroma import Chroma
from langchain.schema import Document

from src.configs.minio import init_minio

MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")
minio_client = init_minio()

def storing_to_vector_db(vector_db:Chroma,documents:list[Document]):
  uuids = [str(uuid4()) for _ in range(len(documents))]
  print(f"Adding {len(documents)} documents to the vector database.")
  vector_db.add_documents(documents= documents, ids=uuids)
  print(f"Successfully added {len(documents)} documents to the vector database with {len(uuids)} unique IDs.")



def search_with_neighbors(vector_db:Chroma,query, k=1, neighbor_window=1):
  retrieve_docs =  vector_db.similarity_search(query,k=k)
  temp = retrieve_docs
  # return retrieve_docs
  all_docs = vector_db._collection.get(include=["documents", "metadatas"])

  docs = [Document(page_content=d, metadata=m) for d, m in zip(all_docs["documents"], all_docs["metadatas"])]

  neighbors = []
  seen_indexes = set()

  for doc in retrieve_docs: 
      idx = next((i for i, d in enumerate(docs) if d.page_content == doc.page_content), None)
      if idx is None:
          continue

      start = max(0, idx - neighbor_window)
      end = min(len(docs), idx + neighbor_window + 1)

      for i in range(start, end):
          if i not in seen_indexes:
              neighbors.append(docs[i])
              seen_indexes.add(i)

  return {
      "context_with_neighbors": neighbors,
      "context": temp
  }


def create_prompt_llm(vector_db:Chroma,query):
  chunks = search_with_neighbors(vector_db,query, k=5, neighbor_window=1)
  sources_pages = list()
  label_exist = set()
  for doc in chunks["context_with_neighbors"]:
    if doc.metadata:
      tag = doc.metadata.get("tag", "Unknown")
      source = doc.metadata.get("source", "Unknown")
      page = doc.metadata.get("page", None)
      if source and page:
        label = f"{tag} Hal {page}"
        if label not in label_exist:
          label_exist.add(label)
          presigned_url = minio_client.presigned_get_object(
            bucket_name=MINIO_BUCKET_NAME,
            object_name=source,
            expires=timedelta(hours=24)
          )
          sources_pages.append({
            "label": label,
            "page": page,
            "link": presigned_url,
          })
      
  
  # Format context from chunks
  context_text = ""
  if chunks.get("context_with_neighbors"):
    context_text = "\n".join([doc.page_content for doc in chunks["context_with_neighbors"]])
  
  # Create formatted prompt string
  template = """Kamu adalah asisten akademik cerdas dari Institut Teknologi Kalimantan (ITK). Jawablah pertanyaan pengguna berdasarkan dokumen yang tersedia. Jika tidak ditemukan jawabannya dalam dokumen, katakan bahwa informasi tersebut tidak tersedia.

Konteks:
{context}

Pertanyaan pengguna:
{question}

Instruksi:
- Gunakan konteks untuk menjawab pertanyaan dengan jelas dan ringkas.
- Konteks-konteks tersebut merupakan konteks dokumen dilingkungan Institut Teknologi Kalimantan atau ITK yang hanya relevan untuk civitas akademika ITK
- Jika informasi tidak ditemukan dalam konteks, balas dengan: "Maaf, informasi tersebut tidak tersedia dalam data akademik ITK yang saya miliki."
- Jangan membuat jawaban dari asumsi atau tebakan."""
  
  formatted_prompt = template.format(context=context_text, question=query)
  return {
    "formatted_prompt": formatted_prompt,
    "sources_pages": sources_pages
  }

def delete_documents_by_source(vector_db: Chroma, source_filename: str):

    try:
        vector_db._collection.delete(where={"source": source_filename})
        print(f"Deleted documents with source: {source_filename}")
    except Exception as e:
        print(f"Error deleting documents by source {source_filename}: {e}")
        raise

def list_sources_in_vector_db(vector_db: Chroma):
    """List all unique source filenames in vector database for debugging"""
    try:
        all_data = vector_db._collection.get()
        sources = set()
        
        if all_data.get("metadatas"):
            for metadata in all_data["metadatas"]:
                if metadata and metadata.get("source"):
                    sources.add(metadata["source"])        
                    vector_db._collection.delete(where={"source": metadata["source"]})
        return list(sources)
    except Exception as e:
        print(f"Error listing sources: {e}")
        return []
