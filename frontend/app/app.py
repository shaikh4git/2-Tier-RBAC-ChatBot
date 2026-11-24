import streamlit as st

from api_client import get_current_user
from components.chat import render_chat
from components.login import render_login


st.set_page_config(
    page_title="Ma'din Public School Assistant, Swalath Nagar, Malappuram",
    page_icon="🔐",
    layout="wide",
)


def logout():
    st.session_state.pop("access_token", None)
    st.session_state.pop("user", None)
    st.session_state.pop("messages", None)
    st.rerun()


def main():
    token = st.session_state.get("access_token")

    if not token:
        render_login()
        return

    try:
        user = get_current_user(token)

    except Exception:
        st.error("Unable to validate your session.")
        logout()
        return

    if not user:
        st.session_state.pop("access_token", None)
        st.session_state.pop("user", None)
        st.warning("Your session has expired. Please log in again.")
        st.rerun()

    st.session_state["user"] = user

    with st.sidebar:
        st.subheader("User information")

        st.write(f"**Username:** {user['username']}")
        st.write(f"**Department:** {user['department'] or 'N/A'}")

        st.write("**Assigned roles:**")

        for role in user["roles"]:
            st.write(f"- {role}")

        st.divider()

        st.button(
            "Logout",
            on_click=logout,
            use_container_width=True,
        )

    render_chat()


if __name__ == "__main__":
    main()