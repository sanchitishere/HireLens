import streamlit as st
from utils.data_state import init_session_state
from utils.auth import do_logout, navigate_to

# Import Views
from views.auth_views import page_login
from views.candidate_views import page_candidate_status, page_company_faq, page_ai_interview
from views.recruitment_views import (
    page_dashboard, page_jd_generator, page_jd_analyzer, page_resume_screening,
    page_candidate_ranking, page_interview_questions, page_candidate_pipeline,
    page_outreach_scheduling, page_hr_assistant
)
from views.talent_views import (
    page_talent_dashboard, page_skills_ld, page_attrition_engagement, page_onboarding_tracker
)

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(page_title="HireLens", page_icon="🧭", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stMarkdown a.header-anchor { display: none !important; }
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a, .stMarkdown h5 a, .stMarkdown h6 a { display: none !important; pointer-events: none; }
    </style>
""", unsafe_allow_html=True)

# Initialize data and state
init_session_state()

# ============================================================================
# SIDEBAR & NAVIGATION
# ============================================================================
if st.session_state.get("logged_in", False):
    st.sidebar.title("🧭 HireLens")
    st.sidebar.caption(f"Welcome, {st.session_state.get('username', '')} ({st.session_state.get('user_role', '')})")
    st.sidebar.divider()

    if st.session_state["user_role"] == "HR":
        MODULES = {
            "AI Recruitment": ["Dashboard", "JD Generator", "JD Analyzer", "Resume Screening", "Candidate Ranking", "Interview Questions", "Candidate Pipeline", "Outreach & Scheduling"],
            "Talent Management": ["Talent Dashboard", "Skills & L&D", "Attrition & Engagement", "Onboarding Tracker"],
            "Global": ["HR Assistant"]
        }
    else:
        MODULES = {
            "Candidate Portal": ["My Application", "AI Interview", "Company FAQ"]
        }

    for module_name, pages in MODULES.items():
        st.sidebar.caption(module_name.upper())
        for page in pages:
            is_active = (st.session_state["current_page"] == page)
            button_type = "primary" if is_active else "secondary"
            if st.sidebar.button(page, key=f"nav_{page}", use_container_width=True, type=button_type):
                navigate_to(page, module_name)
                
    st.sidebar.divider()
    if st.sidebar.button("Logout", use_container_width=True):
        do_logout()

# ============================================================================
# ROUTER
# ============================================================================
PAGES = {
    "Login": page_login,
    "My Application": page_candidate_status,
    "Company FAQ": page_company_faq,
    "Dashboard": page_dashboard,
    "JD Generator": page_jd_generator,
    "JD Analyzer": page_jd_analyzer,
    "Resume Screening": page_resume_screening,
    "Candidate Ranking": page_candidate_ranking,
    "Interview Questions": page_interview_questions,
    "AI Interview": page_ai_interview,
    "Candidate Pipeline": page_candidate_pipeline,
    "Outreach & Scheduling": page_outreach_scheduling,
    "Talent Dashboard": page_talent_dashboard,
    "Skills & L&D": page_skills_ld,
    "Attrition & Engagement": page_attrition_engagement,
    "Onboarding Tracker": page_onboarding_tracker,
    "HR Assistant": page_hr_assistant,
}

if st.session_state["current_page"] in PAGES:
    PAGES[st.session_state["current_page"]]()
