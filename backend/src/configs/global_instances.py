from . import llm, embedding, chroma, minio
from pymongo import AsyncMongoClient

# Global instances
_llama_instance = None
_embedding_instance = None
_vector_db_instance = None
_minio_instance = None
_mongo_client = None

def get_llama_instance(model="llama3.2:latest"):
    """Get or create global Llama instance"""
    global _llama_instance
    if _llama_instance is None:
        _llama_instance = llm.init_llm(model=model)
    return _llama_instance

def get_embedding_instance(model_name="firqaaa/indo-sentence-bert-base"):
    """Get or create global embedding instance"""
    global _embedding_instance
    if _embedding_instance is None:
        _embedding_instance = embedding.init_embedding(model_name=model_name)
    return _embedding_instance

def get_vector_db_instance():
    """Get or create global vector database instance"""
    global _vector_db_instance
    if _vector_db_instance is None:
        embedding_func = get_embedding_instance()
        _vector_db_instance = chroma.init_chroma(embedding_func)
    return _vector_db_instance

def get_minio_instance():
    """Get or create global MinIO instance"""
    global _minio_instance
    if _minio_instance is None:
        _minio_instance = minio.init_minio()
    return _minio_instance

def get_mongo_client():
    """Get or create global MongoDB client"""
    global _mongo_client
    if _mongo_client is None:
        import os
        mongo_url = os.getenv("MONGO_URL")
        _mongo_client = AsyncMongoClient(mongo_url)
    return _mongo_client

def reset_all_instances():
    """Reset all global instances (useful for testing)"""
    global _llama_instance, _embedding_instance, _vector_db_instance, _minio_instance, _mongo_client
    _llama_instance = None
    _embedding_instance = None
    _vector_db_instance = None
    _minio_instance = None
    if _mongo_client:
        _mongo_client.close()
    _mongo_client = None
