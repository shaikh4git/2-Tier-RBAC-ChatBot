# Document Ingestion

This directory contains the standalone document ingestion utility
for the Two-Tier RBAC Chatbot.

## Supported formats

- Markdown
- TXT
- PDF
- DOCX
- PPTX

## Configuration

| Variable | Default |
|---|---|
| QDRANT_URL | http://qdrant.enterprise-chatbot.svc.cluster.local:6333 |
| QDRANT_COLLECTION | madinps_docs |
| EMBEDDING_MODEL | sentence-transformers/all-MiniLM-L6-v2 |
| INCLUDE_DEPARTMENT_DOCUMENTS | false |

## Important

The existing Qdrant collection is reused.

The ingestion script does not create, delete, or recreate a collection.

Do not run ingestion during normal backend deployment.

Run ingestion only when a deliberate document update is required.

## Access classification

Public website documents are available to authenticated users.

Department documents are restricted according to their department
and explicitly assigned roles.

The General department documents are available to Employee and
C-Level roles.

C-Level users can access department documents.

## Execution

Install dependencies:

```bash
pip install -r requirements.txt