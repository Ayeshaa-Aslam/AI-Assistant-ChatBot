import os
import json
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda

load_dotenv()

# Fast embedding model (OpenAI)
embeddings = OpenAIEmbeddings(
    model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
)

# Your old chunk_size=50 was too small. This is a good starting point.
text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)

VECTORSTORE_DIR = "vectorstores"
vector_stores = {}


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _vectorstore_path(category: str) -> str:
    return os.path.join(VECTORSTORE_DIR, category)


def _data_path(category: str) -> str:
    # Matches your filenames: billing_docs.json, technical_docs.json, etc.
    return os.path.join("data", f"{category}_docs.json")


def _load_json_data(category: str):
    path = _data_path(category)
    if not os.path.exists(path):
        print(f"[RETRIEVER] Data file not found: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _extract_text(item) -> str:
    """
    Your JSON files are lists of STRINGS (seen in your screenshot),
    but we also support list of OBJECTS as a fallback.
    """
    if isinstance(item, str):
        return item.strip()

    if isinstance(item, dict):
        text = (
            item.get("text")
            or item.get("content")
            or item.get("answer")
            or item.get("body")
            or item.get("message")
            or ""
        )
        return str(text).strip()

    return ""

def _build_vectorstore_for_category(category: str) -> FAISS:
    rows = _load_json_data(category)

    docs = []
    for item in rows:
        text = _extract_text(item)
        if text:
            docs.append(Document(page_content=text, metadata={"category": category}))

    if not docs:
        raise ValueError(
            f"[RETRIEVER] No valid text found for category '{category}'. "
            f"Check { _data_path(category) } format/content."
        )

    split_docs = text_splitter.split_documents(docs)
    if not split_docs:
        raise ValueError(
            f"[RETRIEVER] Text splitter produced 0 chunks for '{category}'. "
            "Increase chunk_size or check input text."
        )

    vs = FAISS.from_documents(split_docs, embeddings)
    return vs


def load_or_create_vectorstores():
    """
    Loads FAISS vectorstores from disk if present; otherwise builds and saves them.
    """
    _ensure_dir(VECTORSTORE_DIR)

    categories = ["billing", "technical", "security", "general"]

    for category in categories:
        path = _vectorstore_path(category)

        if os.path.exists(path):
            print(f" Loading existing vectorstore for {category}...")
            vector_stores[category] = FAISS.load_local(
                path, embeddings, allow_dangerous_deserialization=True
            )
            print(f"Loaded {category} vectorstore from disk")
        else:
            print(f" Building new vectorstore for {category}...")
            vs = _build_vectorstore_for_category(category)
            vs.save_local(path)
            vector_stores[category] = vs
            print(f"Saved {category} vectorstore to disk")


def retrieve_context(state):
    """
    LangGraph node that retrieves relevant context from the chosen category store.
    """
    category = (state.get("category") or "general").strip().lower()
    query = f"{state.get('subject','')} {state.get('description','')}".strip()

    if category not in vector_stores or vector_stores.get(category) is None:
        return {"retrieved_context": [f"No vectorstore loaded for category: {category}"]}

    docs = vector_stores[category].similarity_search(query, k=3)
    context = [doc.page_content for doc in docs]

    print(f" Found {len(context)} relevant chunks")
    return {"retrieved_context": context}


retriever_node = RunnableLambda(retrieve_context)
