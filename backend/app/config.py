import os


# Application
APP_NAME = "Two-Tier RBAC Chatbot"
APP_VERSION = "1.0.0"


# Qdrant configuration
QDRANT_URL = os.getenv(
    "QDRANT_URL",
    "http://qdrant.enterprise-chatbot.svc.cluster.local:6333",
)

QDRANT_COLLECTION = os.getenv(
    "QDRANT_COLLECTION",
    "madinps_docs",
)


# Embedding configuration
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)


# LLM configuration
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b",
)


# Retrieval configuration
RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "15"))


# JWT configuration
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)
