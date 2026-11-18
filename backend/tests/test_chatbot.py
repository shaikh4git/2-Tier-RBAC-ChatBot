from unittest.mock import MagicMock

from app.chatbot import ChatbotService


def test_greeting_does_not_call_retrieval():
    vector_store = MagicMock()
    llm = MagicMock()

    service = ChatbotService(
        vector_store=vector_store,
        llm=llm,
    )

    result = service.answer_question(
        "hello",
        {"username": "john", "roles": []},
    )

    assert result["sources"] == []
    assert "Hello" in result["answer"]

    vector_store.similarity_search.assert_not_called()
    llm.invoke.assert_not_called()


def test_no_documents_returns_fallback():
    vector_store = MagicMock()
    vector_store.similarity_search.return_value = []

    llm = MagicMock()

    service = ChatbotService(
        vector_store=vector_store,
        llm=llm,
    )

    result = service.answer_question(
        "What are the admission requirements?",
        {"username": "john", "department": "Finance", "roles": []},
    )

    assert result["sources"] == []
    assert "could not find sufficient information" in result["answer"]
    llm.invoke.assert_not_called()


def test_authorized_document_is_retrieved():
    vector_store = MagicMock()

    document = MagicMock()
    document.page_content = "Finance policy information."
    document.metadata = {
        "access_scope": "restricted",
        "allowed_roles": ["Finance"],
        "source": "Finance/policy.pdf",
    }

    vector_store.similarity_search.return_value = [document]

    service = ChatbotService(
        vector_store=vector_store,
        llm=MagicMock(),
    )

    user = {
        "username": "john",
        "department": "Finance",
        "roles": [],
    }

    documents = service.retrieve_documents(
        "finance policy",
        user,
    )

    assert len(documents) == 1