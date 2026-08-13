import streamlit as st
import pandas as pd
from datetime import datetime

FUNNEL_STAGES = ["Applied", "Screening", "Interview", "Offer", "Hired", "Rejected"]

def init_session_state():
    if "roles_df" not in st.session_state:
        st.session_state["roles_df"] = pd.DataFrame([
            {"Role": "Data Scientist", "Department": "Data & AI", "Days Open": 12, "In Pipeline": 5, "Priority": "🔴 Urgent"},
            {"Role": "Backend Engineer", "Department": "Engineering", "Days Open": 30, "In Pipeline": 12, "Priority": "🟡 Medium"},
            {"Role": "Product Manager", "Department": "Product", "Days Open": 5, "In Pipeline": 2, "Priority": "🟢 On Track"},
        ])
    if "candidates_df" not in st.session_state:
        st.session_state["candidates_df"] = pd.DataFrame([
            {"Name": "Riya Sharma", "Email": "riya.sharma@example.com", "Role": "Data Scientist", "Stage": "Interview", "AI Match %": 92, "Applied On": "Jul 10"},
            {"Name": "Aarav Mehta", "Email": "aarav.mehta@example.com", "Role": "Backend Engineer", "Stage": "Screening", "AI Match %": 78, "Applied On": "Jul 18"},
            {"Name": "Kabir Singh", "Email": "kabir.singh@example.com", "Role": "Product Manager", "Stage": "Offer", "AI Match %": 88, "Applied On": "Jul 05"},
        ])
    if "activity_feed" not in st.session_state:
        st.session_state["activity_feed"] = pd.DataFrame(columns=["Activity", "Time"])

    if "employees_df" not in st.session_state:
        st.session_state["employees_df"] = pd.DataFrame([
            {"Employee": "Priya Sharma", "Department": "Engineering", "Role": "Frontend Engineer", "Tenure (yrs)": 2.5, "Risk Score": 35, "Risk Level": "Low", "Engagement Score": 85, "Python": 40, "Cloud": 20, "Communication": 90, "Data Analysis": 10, "Leadership": 40},
            {"Employee": "Vikram Gupta", "Department": "Data & AI", "Role": "Data Analyst", "Tenure (yrs)": 4.1, "Risk Score": 85, "Risk Level": "High", "Engagement Score": 45, "Python": 80, "Cloud": 30, "Communication": 75, "Data Analysis": 95, "Leadership": 50},
            {"Employee": "Ananya Singh", "Department": "Product", "Role": "Product Owner", "Tenure (yrs)": 1.2, "Risk Score": 60, "Risk Level": "Medium", "Engagement Score": 65, "Python": 20, "Cloud": 10, "Communication": 95, "Data Analysis": 60, "Leadership": 85},
            {"Employee": "Rohan Patel", "Department": "Engineering", "Role": "Backend Engineer", "Tenure (yrs)": 3.8, "Risk Score": 45, "Risk Level": "Medium", "Engagement Score": 70, "Python": 90, "Cloud": 85, "Communication": 60, "Data Analysis": 50, "Leadership": 60},
            {"Employee": "Kavya Iyer", "Department": "Data & AI", "Role": "Data Scientist", "Tenure (yrs)": 0.1, "Risk Score": 10, "Risk Level": "Low", "Engagement Score": 95, "Python": 80, "Cloud": 60, "Communication": 80, "Data Analysis": 90, "Leadership": 50},
            {"Employee": "Neha Kapoor", "Department": "Engineering", "Role": "Backend Engineer", "Tenure (yrs)": 0.0, "Risk Score": 5, "Risk Level": "Low", "Engagement Score": 100, "Python": 85, "Cloud": 70, "Communication": 70, "Data Analysis": 60, "Leadership": 60},
        ])
    if "onboarding_df" not in st.session_state:
        st.session_state["onboarding_df"] = pd.DataFrame([
            {"Name": "Kavya Iyer", "Role": "Data Scientist", "Progress": 80, "Tasks Completed": "Offer accepted, IT setup complete"},
            {"Name": "Neha Kapoor", "Role": "Backend Engineer", "Progress": 30, "Tasks Completed": "Offer accepted"},
        ])
    if "survey_df" not in st.session_state:
        weeks = pd.date_range(end=datetime.now(), periods=10, freq="W")
        scores = [65, 68, 70, 69, 72, 75, 74, 76, 78, 80]
        st.session_state["survey_df"] = pd.DataFrame({
            "Week": weeks, "Score": scores, "Sentiment": scores,
            "Comment": ["Need better tools", "", "Good all hands meeting", "", "Onboarding is improving", "", "More clarity needed", "", "Love the new projects", "Great momentum!"]
        })
    if "skill_targets_df" not in st.session_state:
        st.session_state["skill_targets_df"] = pd.DataFrame([
            {"Role": "Frontend Engineer", "Python": 60, "Cloud": 50, "Communication": 90, "Data Analysis": 40, "Leadership": 50},
            {"Role": "Backend Engineer", "Python": 95, "Cloud": 90, "Communication": 70, "Data Analysis": 60, "Leadership": 70},
            {"Role": "Data Analyst", "Python": 85, "Cloud": 60, "Communication": 85, "Data Analysis": 95, "Leadership": 60},
            {"Role": "Product Owner", "Python": 40, "Cloud": 30, "Communication": 100, "Data Analysis": 70, "Leadership": 90},
            {"Role": "Data Scientist", "Python": 90, "Cloud": 70, "Communication": 80, "Data Analysis": 100, "Leadership": 60},
        ])

    if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
    if "user_role" not in st.session_state: st.session_state["user_role"] = None
    if "username" not in st.session_state: st.session_state["username"] = ""

    if "current_module" not in st.session_state: st.session_state["current_module"] = "Authentication"
    if "current_page" not in st.session_state: st.session_state["current_page"] = "Login"


def get_priority_roles(): return st.session_state["roles_df"]
def get_candidates(): return st.session_state["candidates_df"]
def get_activity_feed(): return st.session_state["activity_feed"]

def get_unique_roles():
    roles = []
    if "roles_df" in st.session_state and not st.session_state["roles_df"].empty and "Role" in st.session_state["roles_df"].columns:
        roles = st.session_state["roles_df"]["Role"].dropna().unique().tolist()
    if not roles: roles = ["Software Engineer", "Data Scientist", "Product Manager"]
    return roles

def get_unique_departments():
    depts = []
    if "roles_df" in st.session_state and not st.session_state["roles_df"].empty and "Department" in st.session_state["roles_df"].columns:
        depts = st.session_state["roles_df"]["Department"].dropna().unique().tolist()
    if not depts: depts = ["Engineering", "Data & AI", "Product"]
    return depts
