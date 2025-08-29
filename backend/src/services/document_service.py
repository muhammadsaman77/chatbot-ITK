
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.utils import filter_complex_metadata

import re
def extract_text_from_pdf(file_path,source) -> list:
    loader = PyMuPDFLoader(file_path)
    text_pages = []
    for page in loader.lazy_load():
        text = page.page_content
        if text.strip():
            text_pages.append(Document(page_content=text, metadata={
                "page": page.metadata["page"],
                "source": source
            }))

    return text_pages

def clean_text(text: str) -> str:
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def chunking_document(documents, chunk_size=128, chunk_overlap=0):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "]
    )
    chunked_docs = []
    for doc in documents:
        cleaned_text = clean_text(doc.page_content)
        splits = text_splitter.split_text(cleaned_text)

        for i, chunk in enumerate(splits):
            chunked_docs.append(Document(
                page_content=chunk,
                metadata={
                    **doc.metadata,
                    "chunk_id": i
                }
            ))

    return filter_complex_metadata(chunked_docs)

