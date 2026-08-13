import streamlit as st
import pandas as pd
from utils.llm import call_llama
from utils.data_state import get_unique_roles, get_candidates

def page_candidate_status():
    st.title("My Application")
    username = st.session_state.get("username", "")
    st.caption(f"Welcome back, {username}!")
    
    cands = get_candidates()
    my_apps = cands[cands["Name"].str.lower() == username.lower()] if not cands.empty and "Name" in cands.columns else pd.DataFrame()
    
    if my_apps.empty:
        st.info("We couldn't find any active applications under your exact name. Please check back later.")
    else:
        st.write("### Your Active Roles")
        for _, row in my_apps.iterrows():
            with st.container(border=True):
                st.subheader(row.get("Role", "Role"))
                stage = row.get("Stage", "Unknown")
                st.write(f"**Current Status:** {stage}")
                
                stages = ["Applied", "Screening", "Interview", "Offer", "Hired", "Rejected"]
                if stage in stages:
                    idx = stages.index(stage)
                    if stage == "Rejected":
                        st.error("Unfortunately, we are moving forward with other candidates at this time.")
                    else:
                        st.progress(min((idx + 1) * 20, 100))
                        
                if stage == "Interview":
                    st.success("🎉 You've been selected for an interview! Please proceed to the AI Interview simulator to practice.")

def page_company_faq():
    st.title("Company FAQ & Culture")
    st.caption("Ask our AI about our company culture, benefits, work-life balance, and what it's like to work here!")
    
    if "faq_history" not in st.session_state:
        st.session_state.faq_history = [{"role": "assistant", "text": "Hi there! I'm the Company Culture Assistant. What would you like to know about working with us?"}]

    for msg in st.session_state.faq_history:
        with st.chat_message(msg["role"]): st.write(msg["text"])

    user_input = st.chat_input("Ask about benefits, culture, or the interview process...")
    if user_input:
        st.session_state.faq_history.append({"role": "user", "text": user_input})
        with st.chat_message("user"): st.write(user_input)
        
        system_prompt = (
            "You are a friendly and enthusiastic Culture Ambassador for a modern tech company. "
            "Your goal is to answer candidate questions about the company's culture, benefits, work-life balance, and values. "
            "Our company offers: Remote-first work, flexible hours, comprehensive health insurance, mental health days, a learning & development stipend, "
            "and a highly collaborative environment. We value transparency, ownership, and diversity. "
            "Keep your answers engaging, encouraging, and concise. Do not answer questions unrelated to the company or the hiring process."
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        for m in st.session_state.faq_history: messages.append({"role": m["role"], "content": m["text"]})
        
        with st.chat_message("assistant"):
            with st.spinner("Typing..."):
                reply, err = call_llama(messages, temperature=0.5)
            if err: reply = f"⚠️ {err}"
            st.write(reply)
            
        st.session_state.faq_history.append({"role": "assistant", "text": reply})

def page_ai_interview():
    st.title("AI Interview Simulator")
    st.caption("Conduct AI-powered interview simulations with text or voice.")
    
    try:
        from audiorecorder import audiorecorder
        has_audio = True
    except ImportError:
        has_audio = False
        
    role = st.selectbox("Role to Interview For", get_unique_roles(), key="ai_int_role")
    
    # Reset interview if role changes or if not started
    if "interview_role" not in st.session_state or st.session_state.interview_role != role:
        st.session_state.interview_role = role
        st.session_state.interview_history = [
            {"role": "assistant", "content": f"Hello! I'm your AI interviewer. Let's start the interview for the {role} position. Could you briefly introduce yourself?"}
        ]
        
    # Display chat
    for msg in st.session_state.interview_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    # Input handling
    user_text = st.chat_input("Type your answer...")
    
    if has_audio:
        st.write("---")
        st.caption("Or answer using voice:")
        audio = audiorecorder("🎤 Start Recording", "🛑 Stop Recording")
        if len(audio) > 0:
            st.info("Audio recorded! (Note: Speech-to-text requires local Whisper or an API. For this demo, voice processing is mocked.)")
            user_text = "[Voice Input Received - 'I am very excited about this role and have the relevant skills.']"
            
    if user_text:
        st.session_state.interview_history.append({"role": "user", "content": user_text})
        with st.chat_message("user"): st.write(user_text)
        
        with st.chat_message("assistant"):
            with st.spinner("Evaluating and thinking of next question..."):
                prompt_messages = [
                    {"role": "system", "content": f"You are an expert HR recruiter interviewing a candidate for a {role} role. Ask one relevant interview question at a time. Keep it under 3 sentences. Be professional and evaluate their previous answer."}
                ] + st.session_state.interview_history
                
                reply, err = call_llama(prompt_messages, temperature=0.6)
                if err:
                    st.error(err)
                else:
                    st.write(reply)
                    st.session_state.interview_history.append({"role": "assistant", "content": reply})
