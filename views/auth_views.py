import streamlit as st
from utils.auth import do_login

def page_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: #6c5ce7;'>🧭 HireLens</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: gray;'>Intelligent Talent Platform</h4>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.subheader("Welcome Back")
            st.caption("Sign in to continue to your dashboard")
            
            username = st.text_input("Username / Full Name", placeholder="e.g. admin or Riya Sharma")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In", type="primary", use_container_width=True):
                if username.strip() and password.strip():
                    # Retrieve passwords from st.secrets if available, otherwise use demo defaults
                    admin_pw = st.secrets.get("admin_password", "admin123")
                    candidate_pw = st.secrets.get("candidate_password", "candidate123")
                    
                    if username.strip().lower() == "admin" and password == admin_pw:
                        do_login("HR", "Admin")
                    elif password == candidate_pw:
                        do_login("Candidate", username.strip())
                    else:
                        st.error("Invalid credentials.")
                else:
                    st.error("Please enter both username and password.")
                    
        st.markdown("<p style='text-align: center; color: gray; font-size: small; margin-top: 10px;'>Secure AI-Powered Hiring Portal</p>", unsafe_allow_html=True)
