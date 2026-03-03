import os
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

CORPUS_DIR = Path("data/corpus")
INDEX_PATH = Path("data/faiss_index")

def build_or_load_index() -> FAISS:
    embeddings = OpenAIEmbeddings()
    if INDEX_PATH.exists():
        return FAISS.load_local(str(INDEX_PATH), embeddings,
                                allow_dangerous_deserialization=True)

    docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)

    for f in CORPUS_DIR.glob("**/*"):
        if f.suffix == ".pdf":
            loader = PyPDFLoader(str(f))
        elif f.suffix in {".txt", ".md"}:
            loader = TextLoader(str(f))
        else:
            continue
        docs.extend(splitter.split_documents(loader.load()))

    if not docs:
        return None

    store = FAISS.from_documents(docs, embeddings)
    store.save_local(str(INDEX_PATH))
    return store


def retrieve_context(query: str, k: int = 6) -> tuple[str, list[dict]]:
    store = build_or_load_index()
    if store is None:
        return "", []

    results = store.similarity_search_with_score(query, k=k)
    sources = []
    chunks = []

    for doc, score in results:
        chunks.append(doc.page_content)
        sources.append({
            "source": doc.metadata.get("source", "Unknown"),
            "page":   doc.metadata.get("page", "—"),
            "relevance": round(1 - score, 3),  # cosine-style normalisation
        })

    return "\n\n".join(chunks), sources
