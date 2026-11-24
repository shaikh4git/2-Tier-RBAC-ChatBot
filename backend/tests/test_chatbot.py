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

def test_private_collection_is_searched_for_authenticated_user():
    shared_store = MagicMock()
    shared_store.similarity_search.return_value = []

    private_store = MagicMock()

    document = MagicMock()
    document.page_content = "Shaikh Shamsul Huda profile."
    document.metadata = {
        "access_scope": "private",
        "owner": "shaikh",
        "allowed_users": ["shaikh"],
        "allowed_roles": [],
        "source": "Users/shaikh/shaikh_private_profile.md",
    }

    private_store.similarity_search.return_value = [document]

    factory = MagicMock(return_value=private_store)

    service = ChatbotService(
        vector_store=shared_store,
        llm=MagicMock(),
        private_vector_store_factory=factory,
    )

    documents = service.retrieve_documents(
        "Who is Shaikh Shamsul Huda?",
        {"username": "shaikh", "department": "Private", "roles": ["Owner"]},
    )

    factory.assert_called_once_with("shaikh")
    private_store.similarity_search.assert_called_once()

    assert len(documents) == 1
    assert documents[0].page_content == "Shaikh Shamsul Huda profile."


def test_private_collection_rejects_another_users_document():
    shared_store = MagicMock()
    shared_store.similarity_search.return_value = []

    private_store = MagicMock()

    document = MagicMock()
    document.page_content = "Shaikh's private profile."
    document.metadata = {
        "access_scope": "private",
        "owner": "shaikh",
        "allowed_users": ["shaikh"],
        "allowed_roles": [],
    }

    # Simulate an incorrectly returned candidate. The application-side
    # authorization check must still reject it.
    private_store.similarity_search.return_value = [document]

    service = ChatbotService(
        vector_store=shared_store,
        llm=MagicMock(),
        private_vector_store_factory=MagicMock(return_value=private_store),
    )

    documents = service.retrieve_documents(
        "Who is Shaikh?",
        {"username": "john", "department": "Finance", "roles": []},
    )

    assert documents == []


def test_missing_private_collection_does_not_break_shared_search():
    shared_store = MagicMock()
    shared_store.similarity_search.return_value = []

    factory = MagicMock(return_value=None)

    service = ChatbotService(
        vector_store=shared_store,
        llm=MagicMock(),
        private_vector_store_factory=factory,
    )

    documents = service.retrieve_documents(
        "What is my profile?",
        {"username": "shaikh", "department": "Private", "roles": ["Owner"]},
    )

    factory.assert_called_once_with("shaikh")
    assert documents == []