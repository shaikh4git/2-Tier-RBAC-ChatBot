import streamlit as st

from api_client import ask_question


def render_chat():
    st.title("Institutional Chatbot")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                with st.expander("Sources"):
                    for source in message["sources"]:
                        st.write(source)

    question = st.chat_input(
        "Ask a question..."
    )

    if not question:
        return

    st.session_state["messages"].append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching authorized documents..."):
            try:
                result = ask_question(
                    st.session_state["access_token"],
                    question,
                )

                if result is None:
                    st.session_state.pop("access_token", None)
                    st.error("Your session has expired. Please sign in again.")
                    st.rerun()

                answer = result["answer"]
                sources = result.get("sources", [])

                st.markdown(answer)

                if sources:
                    with st.expander("Sources"):
                        for source in sources:
                            st.write(source)

                st.session_state["messages"].append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

            except Exception:
                st.error(
                    "Unable to process your request. "
                    "Please try again."
                )