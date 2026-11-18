import logging
from contextlib import asynccontextmanager

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from .auth import (
    authenticate,
    create_access_token,
    get_current_user_from_token,
)
from .chatbot import ChatbotService
from .config import (
    APP_NAME,
    APP_VERSION,
    CORS_ORIGINS,
)


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize application resources when FastAPI starts.
    """
    logger.info("Starting %s", APP_NAME)

    try:
        app.state.chatbot = ChatbotService.create()
        app.state.ready = True

        logger.info("Chatbot service initialized")

    except Exception:
        app.state.chatbot = None
        app.state.ready = False

        logger.exception("Chatbot initialization failed")

    yield

    app.state.chatbot = None

    logger.info("Application shutdown completed")


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Authenticate the JWT and retrieve current roles from the backend
    user database.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_current_user_from_token(
        credentials.credentials
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@app.get("/health/live")
def liveness():
    return {
        "status": "alive",
        "application": APP_NAME,
    }


@app.get("/health/ready")
def readiness():
    if not getattr(app.state, "ready", False):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Application is not ready",
        )

    return {
        "status": "ready",
        "application": APP_NAME,
    }


@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest):
    user = authenticate(
        request.username,
        request.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(user)

    from .config import JWT_ACCESS_TOKEN_EXPIRE_MINUTES

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@app.get("/auth/me")
def get_me(user=Depends(get_current_user)):
    """
    Return the current user identity and backend-derived roles.
    """
    return {
        "username": user["username"],
        "department": user["department"],
        "roles": user["roles"],
    }


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    user=Depends(get_current_user),
):
    chatbot = getattr(app.state, "chatbot", None)

    if chatbot is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot service is unavailable",
        )

    result = chatbot.answer_question(
        request.question,
        user,
    )

    return result