# Two-Tier RBAC Chatbot

A retrieval-augmented institutional chatbot with backend-enforced
Role-Based Access Control.

## Architecture

- Frontend: Streamlit Community Cloud
- Backend: FastAPI
- Authentication: bcrypt and JWT
- Authorization: Role-Based Access Control
- Vector database: Existing Qdrant deployment
- Embeddings: sentence-transformers/all-MiniLM-L6-v2
- LLM: Groq openai/gpt-oss-20b
- Orchestration: Kubernetes
- CI: GitHub Actions

## Existing infrastructure integration

The application reuses the existing Qdrant deployment.

Qdrant namespace:

    enterprise-chatbot

Qdrant service:

    qdrant.enterprise-chatbot.svc.cluster.local:6333

Collection:

    madinps_docs

The application does not create or recreate the collection.

## Application structure

    backend/       FastAPI backend
    frontend/      Streamlit frontend
    ingestion/     Document ingestion utility
    k8s/           Kubernetes manifests
    .github/       CI workflows

## Authentication

Users are configured through the Kubernetes Secret
CHATBOT_USERS_JSON environment variable.

Passwords must be stored as bcrypt hashes.

The backend issues signed JWT access tokens.

The backend reloads the current user's department and roles from
the user database when validating each request.

The frontend cannot assign or override user roles.

## RBAC behavior

Every authenticated user receives the Employee role.

The user's department is also treated as a role.

Explicitly assigned roles are retained.

Documents can be:

- Accessible to all authenticated users.
- Restricted to specific roles.

The backend applies Qdrant metadata filtering and an additional
application-side access check.

## Local backend development

Create a virtual environment:

    cd backend
    python3.11 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Configure environment variables before starting the backend.

Start:

    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

API documentation:

    http://127.0.0.1:8000/docs

Health:

    http://127.0.0.1:8000/health/live

## Backend tests

From the repository root:

    cd backend
    PYTHONPATH=. pytest -v tests/

## Docker image

Build locally:

    docker build -t shaikhdocker/two-tier-rbac-backend:dev ./backend

## Kubernetes deployment

Create the namespace:

    kubectl apply -f k8s/namespace.yaml

Create the ConfigMap:

    kubectl apply -f k8s/configmap.yaml

Create the Kubernetes Secret separately.

Apply the Deployment and Service:

    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml

Check:

    kubectl get all -n two-tier-rbac

## Security

- Do not commit API keys or JWT secrets.
- Do not commit real Kubernetes Secret manifests.
- Do not expose Qdrant publicly.
- Use HTTPS for external API access.
- Validate user identity and roles on the backend.
- Treat retrieved documents as untrusted input.
- Restrict CORS to the frontend origin for production.

## GitOps

Kubernetes application deployment will eventually be managed
through the separate repository:

    2-Tier-RBAC-ChatBot-GitOps

The application repository and existing Enterprise-RBAC
repositories remain independent.