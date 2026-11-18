import hashlib
import os
import uuid

from pathlib import Path

from docling.document_converter import DocumentConverter

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

from qdrant_client import QdrantClient


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOCUMENTS_ROOT = Path(
    os.getenv(
        "DOCUMENTS_ROOT",
        str(PROJECT_ROOT / "documents"),
    )
)

QDRANT_URL = os.getenv(
    "QDRANT_URL",
    "http://qdrant.enterprise-chatbot.svc.cluster.local:6333",
)

QDRANT_COLLECTION = os.getenv(
    "QDRANT_COLLECTION",
    "madinps_docs",
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

INCLUDE_DEPARTMENT_DOCUMENTS = (
    os.getenv(
        "INCLUDE_DEPARTMENT_DOCUMENTS",
        "false",
    ).lower() == "true"
)

WEBSITE_DOMAIN = "madinps.edu.in"

SUPPORTED_EXTENSIONS = {
    ".md",
    ".txt",
    ".pdf",
    ".docx",
    ".pptx",
}

CHUNK_SIZE = 900
CHUNK_OVERLAP = 120


def load_file(path):
    """
    Extract document content.
    """
    extension = path.suffix.lower()

    if extension in {".md", ".txt"}:
        return path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    converter = DocumentConverter()

    result = converter.convert(str(path))

    return result.document.export_to_markdown()


def extract_source_url(content):
    """
    Extract an optional source_url header from Markdown content.
    """
    for line in content.splitlines()[:10]:
        line = line.strip()

        if line.startswith("source_url:"):
            return line.split(":", 1)[1].strip()

    return None


def classify_document(relative_path, source_url=None):
    """
    Apply the original public/department document access rules.
    """
    if source_url:
        if not source_url.startswith("https://"):
            raise ValueError("Only HTTPS website URLs are permitted")

        from urllib.parse import urlparse

        parsed = urlparse(source_url)

        if parsed.hostname != WEBSITE_DOMAIN:
            raise ValueError(
                f"Unapproved website domain: {parsed.hostname}"
            )

        return {
            "source": relative_path.as_posix(),
            "url": source_url,
            "domain": WEBSITE_DOMAIN,
            "department": "Public",
            "access_scope": "authenticated",
            "allowed_roles": [],
            "content_type": "website",
        }

    department = (
        relative_path.parts[0]
        if len(relative_path.parts) > 1
        else "General"
    )

    if department == "General":
        allowed_roles = ["Employee", "C-Level"]
    else:
        allowed_roles = [department, "C-Level"]

    return {
        "source": relative_path.as_posix(),
        "department": department,
        "access_scope": "restricted",
        "allowed_roles": allowed_roles,
        "content_type": "department_document",
    }


def load_documents():
    """
    Read the document directory and construct LangChain documents.
    """
    documents = []

    for path in DOCUMENTS_ROOT.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        relative_path = path.relative_to(DOCUMENTS_ROOT)

        try:
            content = load_file(path)

            if not content.strip():
                continue

            source_url = extract_source_url(content)

            # Keep the original default behavior: department
            # documents are excluded unless explicitly enabled.
            if (
                not source_url
                and not INCLUDE_DEPARTMENT_DOCUMENTS
            ):
                continue

            metadata = classify_document(
                relative_path,
                source_url,
            )

            documents.append(
                Document(
                    page_content=content,
                    metadata=metadata,
                )
            )

        except Exception as exc:
            print(f"Skipping {path}: {exc}")

    return documents


def stable_chunk_id(document, index):
    """
    Create a deterministic ID for a document chunk.
    """
    source = document.metadata.get("source", "")

    content_hash = hashlib.sha256(
        document.page_content.encode("utf-8")
    ).hexdigest()

    identity = f"{source}:{index}:{content_hash}"

    return str(
        uuid.uuid5(
            uuid.NAMESPACE_URL,
            identity,
        )
    )


def ingest():
    """
    Add document chunks to the existing Qdrant collection.

    This function deliberately does not recreate or delete a collection.
    """
    client = QdrantClient(
        url=QDRANT_URL,
        timeout=30,
    )

    if not client.collection_exists(QDRANT_COLLECTION):
        raise RuntimeError(
            f"Collection {QDRANT_COLLECTION} does not exist. "
            "This utility will not create it automatically."
        )

    documents = load_documents()

    if not documents:
        print("No documents found for ingestion.")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    chunks = splitter.split_documents(documents)

    ids = []

    for index, chunk in enumerate(chunks):
        ids.append(
            stable_chunk_id(
                chunk,
                index,
            )
        )

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=QDRANT_COLLECTION,
        embedding=embeddings,
    )

    vector_store.add_documents(
        documents=chunks,
        ids=ids,
    )

    print(f"Documents loaded: {len(documents)}")
    print(f"Chunks added: {len(chunks)}")
    print(f"Collection: {QDRANT_COLLECTION}")


if __name__ == "__main__":
    ingest()