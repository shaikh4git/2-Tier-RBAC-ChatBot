import streamlit as st

from api_client import login


def render_login():
    st.title("Ma'din Public School Assistant, Swalath Nagar, Malappuram")

    st.subheader("Sign in")

    with st.form("login_form"):
        username = st.text_input(
            "Username",
            autocomplete="username",
        )

        password = st.text_input(
            "Password",
            type="password",
            autocomplete="current-password",
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
        )

    if submitted:
        if not username or not password:
            st.warning("Please enter your username and password.")
            return

        try:
            result = login(username, password)

            if not result:
                st.error("Invalid username or password.")
                return

            st.session_state["access_token"] = result["access_token"]

            st.rerun()

        except Exception:
            st.error(
                "Unable to connect to the authentication service. "
                "Please try again later."
            )