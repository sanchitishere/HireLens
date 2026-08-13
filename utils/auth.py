import streamlit as st

def navigate_to(page, module):
    st.session_state["current_page"] = page
    st.session_state["current_module"] = module
    st.rerun()

def do_login(role, username):
    st.session_state["logged_in"] = True
    st.session_state["user_role"] = role
    st.session_state["username"] = username
    if role == "HR":
        st.session_state["current_page"] = "Dashboard"
        st.session_state["current_module"] = "AI Recruitment"
    else:
        st.session_state["current_page"] = "My Application"
        st.session_state["current_module"] = "Candidate Portal"
    st.rerun()

def do_logout():
    st.session_state["logged_in"] = False
    st.session_state["user_role"] = None
    st.session_state["username"] = ""
    st.session_state["current_page"] = "Login"
    st.session_state["current_module"] = "Authentication"
    st.rerun()
