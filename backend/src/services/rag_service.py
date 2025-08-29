from uuid import uuid4
from langchain_chroma import Chroma
from langchain.schema import Document

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

  for doc in retrieve_docs:  # ✅ tidak unpack
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
  return formatted_prompt

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
        
        return list(sources)
    except Exception as e:
        print(f"Error listing sources: {e}")
        return []
