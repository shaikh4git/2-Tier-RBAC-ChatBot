import os

APP_NAME = "Two-Tier RBAC Chatbot"
APP_VERSION = "1.0.0"

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

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b",
)

RETRIEVAL_K = int(os.getenv("RETRIEVAL_K", "15"))

JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

JWT_ALGORITHM = "HS256"

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

CHATBOT_USERS_JSON = os.getenv("CHATBOT_USERS_JSON", "{}")

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]