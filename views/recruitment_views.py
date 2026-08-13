import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from utils.llm import call_llama
from utils.file_parser import extract_text_from_file
from utils.data_state import get_unique_roles, get_unique_departments, get_candidates, get_priority_roles, FUNNEL_STAGES
from utils.auth import navigate_to

def page_dashboard():
    st.title("Command Center")
    st.caption("Where things stand right now — manage your data and review metrics.")

    # Sync 'In Pipeline' counts dynamically
    if not st.session_state["roles_df"].empty and not st.session_state["candidates_df"].empty:
        cands = st.session_state["candidates_df"]
        roles = st.session_state["roles_df"]
        if "Role" in roles.columns and "Stage" in cands.columns:
            active_cands = cands[~cands["Stage"].isin(["Hired", "Rejected"])]
            counts = active_cands["Role"].value_counts()
            roles["In Pipeline"] = roles["Role"].map(counts).fillna(0).astype(int)
            st.session_state["roles_df"] = roles

    qa1, qa2, qa3, qa4 = st.columns(4)
    if qa1.button("Draft a JD", use_container_width=True): navigate_to("JD Generator", "AI Recruitment")
    if qa2.button("Screen a Resume", use_container_width=True): navigate_to("Resume Screening", "AI Recruitment")
    if qa3.button("Prep Interview Qs", use_container_width=True): navigate_to("Interview Questions", "AI Recruitment")
    if qa4.button("Ask HR Assistant", use_container_width=True): navigate_to("HR Assistant", "Global")

    st.write("")
    with st.expander("🛠️ Manage Organization Data", expanded=True):
        t1, t2, t3, t4, t5 = st.tabs(["Priority Roles", "Candidates Pipeline", "Employees", "Activity Feed", "Skill Targets"])
        with t1: st.session_state["roles_df"] = st.data_editor(st.session_state["roles_df"], num_rows="dynamic", use_container_width=True)
        with t2: st.session_state["candidates_df"] = st.data_editor(st.session_state["candidates_df"], num_rows="dynamic", use_container_width=True)
        with t3: st.session_state["employees_df"] = st.data_editor(st.session_state["employees_df"], num_rows="dynamic", use_container_width=True)
        with t4: st.session_state["activity_feed"] = st.data_editor(st.session_state["activity_feed"], num_rows="dynamic", use_container_width=True)
        with t5: st.session_state["skill_targets_df"] = st.data_editor(st.session_state["skill_targets_df"], num_rows="dynamic", use_container_width=True)

    st.write("")
    m1, m2, m3, m4 = st.columns(4)
    roles, candidates = get_priority_roles(), get_candidates()
    open_reqs, total_cands = len(roles), len(candidates)
    active_interviews = len(candidates[candidates["Stage"] == "Interview"]) if not candidates.empty and "Stage" in candidates.columns else 0
    
    m1.metric("Open Requisitions", str(open_reqs))
    m2.metric("Total Candidates", str(total_cands))
    m3.metric("Active Interviews", str(active_interviews))
    m4.metric("Avg. Time to Hire", "N/A")

    st.write("")
    left, right = st.columns([1.4, 1])
    with left:
        st.subheader("Pipeline Health")
        stages = FUNNEL_STAGES[::-1]
        values = [candidates["Stage"].value_counts().get(s, 0) for s in stages] if not candidates.empty and "Stage" in candidates.columns else [0]*len(stages)
        colors = ["#e74c3c", "#3ac6b9", "#ff6b9d", "#ffb020", "#8b7bf0", "#6c5ce7"]
        fig = go.Figure(go.Bar(
            y=stages, x=values, orientation="h", marker_color=colors,
            text=[f"{v}" for v in values], textposition="outside",
        ))
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300, xaxis_title=None, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Departments by Open Roles")
        if not roles.empty and "Department" in roles.columns:
            dep_counts = roles["Department"].value_counts().reset_index()
            dep_counts.columns = ["Department", "Openings"]
            fig2 = px.bar(dep_counts, x="Openings", y="Department", orientation="h", color="Openings", color_continuous_scale="Purples", text="Openings")
            fig2.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300, coloraxis_showscale=False, xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig2, use_container_width=True)

def page_resume_screening():
    st.title("Resume Screening & Profiling")
    st.caption("Upload a resume to extract structured profiles, analyze skill gaps, and score candidates.")

    if "current_screening" not in st.session_state:
        st.session_state["current_screening"] = None

    if st.session_state["current_screening"] is None:
        role = st.selectbox("Target Role", get_unique_roles())
        
        # Optional: Use analyzed JD if available
        use_jd = False
        jd_context = ""
        if "analyzed_jd" in st.session_state:
            jd = st.session_state["analyzed_jd"]
            st.info(f"Using active JD Context: {jd.get('job_title')}")
            use_jd = st.checkbox("Compare against active JD", value=True)
            if use_jd:
                jd_context = f"\n\nJob Requirements:\n{json.dumps(jd, indent=2)}\nEvaluate the candidate strictly against these requirements."

        uploaded = st.file_uploader("Upload Resume (PDF / DOCX)", type=["pdf", "docx"])
        run = st.button("Run AI Screening", type="primary")

        if run and uploaded is not None and role:
            with st.spinner("Parsing and analyzing resume..."):
                resume_text = extract_text_from_file(uploaded)
                
                prompt = (
                    f"You are an AI resume screener. Evaluate this candidate for the role of '{role}'. "
                    f"Resume file name: {uploaded.name}.\n\nResume Text:\n{resume_text}{jd_context}\n\n"
                    "Extract the candidate's profile and provide an evaluation in strictly valid JSON format. "
                    "Do not include markdown blocks or comments. Output ONLY the raw JSON object.\n"
                    "Schema:\n"
                    "{\n"
                    "  \"education\": \"string (highest degree & institution)\",\n"
                    "  \"skills\": [\"skill1\", \"skill2\"],\n"
                    "  \"certifications\": [\"cert1\", \"cert2\"],\n"
                    "  \"experience_summary\": \"string (brief summary of work history)\",\n"
                    "  \"projects\": [\"project1\"],\n"
                    "  \"overall_match_score\": 75,\n"
                    "  \"missing_skills\": [\"skill1\"],\n"
                    "  \"highlights\": [\"strength1\", \"strength2\"],\n"
                    "  \"gaps_to_probe\": [\"gap1\", \"gap2\"]\n"
                    "}"
                )
                
                response, err = call_llama([{"role": "user", "content": prompt}], temperature=0.1)
                
                if err:
                    st.error(err)
                else:
                    try:
                        # Clean up response
                        if response.startswith("```json"): response = response[7:]
                        if response.startswith("```"): response = response[3:]
                        if response.endswith("```"): response = response[:-3]
                            
                        parsed = json.loads(response.strip())
                        cand_name = uploaded.name.replace(".pdf", "").replace(".docx", "").replace("_", " ").title()
                        ai_score = parsed.get("overall_match_score", 75)
                        
                        st.session_state["current_screening"] = {
                            "name": cand_name, "role": role, "score": ai_score, "profile": parsed
                        }
                        
                        # Add as screening internally
                        new_row = pd.DataFrame([{
                            "Name": cand_name, "Role": role, "Stage": "Screening", "AI Match %": ai_score, "Applied On": datetime.now().strftime("%b %d")
                        }])
                        st.session_state["candidates_df"] = pd.concat([st.session_state["candidates_df"], new_row], ignore_index=True)
                        st.rerun()
                    except json.JSONDecodeError:
                        st.error("Failed to parse the LLM output as JSON. Please try again.")
                        st.text(response)
                        
        elif run:
            st.warning("Please provide a Target Role and upload a resume file first.")
    
    else:
        # Approval flow & Display Profile
        screening = st.session_state["current_screening"]
        p = screening["profile"]
        
        c_left, c_right = st.columns([2, 1])
        with c_left:
            st.subheader(f"{screening['name']}")
            st.caption(f"Applied for: {screening['role']}")
        with c_right:
            st.metric("AI Match Score", f"{screening['score']}%")

        # Display Structured Profile
        st.write("### Candidate Profile")
        t1, t2, t3 = st.tabs(["Overview", "Evaluation", "Skill Gaps"])
        
        with t1:
            st.write("**Education:**", p.get("education", "N/A"))
            st.write("**Experience Summary:**", p.get("experience_summary", "N/A"))
            
            st.write("**Skills:**")
            st.write(", ".join([f"`{s}`" for s in p.get("skills", [])]))
            
            if p.get("certifications"):
                st.write("**Certifications:**")
                for c in p.get("certifications", []): st.write(f"- {c}")
            
            if p.get("projects"):
                st.write("**Projects:**")
                for prj in p.get("projects", []): st.write(f"- {prj}")

        with t2:
            st.write("**Highlights:**")
            for h in p.get("highlights", []): st.success(f"✓ {h}")
            st.write("**Gaps to Probe:**")
            for g in p.get("gaps_to_probe", []): st.warning(f"! {g}")
            
        with t3:
            missing = p.get("missing_skills", [])
            if missing:
                st.write("The candidate is missing these key skills:")
                for m in missing: st.error(f"- {m}")
                st.info("💡 **Recommended Training:** Assign the relevant tracks in the Talent Dashboard if hired.")
            else:
                st.success("No major skill gaps identified based on the requirements.")
        
        st.divider()
        st.write("### Decision")
        st.caption("Update the candidate's status in the central pipeline.")
        c1, c2 = st.columns(2)
        
        if c1.button("Approve for Interview", use_container_width=True, type="primary"):
            df = st.session_state["candidates_df"]
            idx = df[(df["Name"] == screening["name"]) & (df["Role"] == screening["role"])].index
            if not idx.empty:
                df.at[idx[-1], "Stage"] = "Interview"
                st.session_state["candidates_df"] = df
            st.session_state["current_screening"] = None
            st.rerun()
            
        if c2.button("Reject", use_container_width=True):
            df = st.session_state["candidates_df"]
            idx = df[(df["Name"] == screening["name"]) & (df["Role"] == screening["role"])].index
            if not idx.empty:
                df.at[idx[-1], "Stage"] = "Rejected"
                st.session_state["candidates_df"] = df
            st.session_state["current_screening"] = None
            st.rerun()


def page_candidate_pipeline():
    st.title("Candidate Pipeline")
    st.caption("Overview of where every candidate stands.")
    df = get_candidates()
    
    if df.empty or "Stage" not in df.columns:
        st.info("No candidates in the pipeline currently.")
        return

    cols = st.columns(len(FUNNEL_STAGES))
    for col, stage in zip(cols, FUNNEL_STAGES):
        with col:
            sub = df[df["Stage"] == stage]
            st.markdown(f"**{stage} ({len(sub)})**")
            for _, row in sub.iterrows():
                with st.container(border=True):
                    st.write(f"**{row.get('Name', 'Unknown')}**")
                    st.caption(row.get('Role', 'Unspecified'))
                    color = "green" if row.get('AI Match %', 0) > 80 else "orange" if row.get('AI Match %', 0) > 60 else "red"
                    st.markdown(f"<span style='color:{color}'>Match: {row.get('AI Match %', 'N/A')}%</span>", unsafe_allow_html=True)
                    
                    if stage not in ["Hired", "Rejected"]:
                        c1, c2 = st.columns(2)
                        next_idx = FUNNEL_STAGES.index(stage) + 1
                        next_stage = FUNNEL_STAGES[next_idx] if next_idx < len(FUNNEL_STAGES)-1 else "Hired"
                        
                        if c1.button("Proceed", key=f"p_{row['Name']}_{stage}", help=f"Proceed to {next_stage}", use_container_width=True):
                            idx = df[df["Name"] == row["Name"]].index[0]
                            st.session_state["candidates_df"].at[idx, "Stage"] = next_stage
                            new_act = pd.DataFrame([{"Activity": f"Promoted {row['Name']} to {next_stage}", "Time": datetime.now().strftime("%I:%M %p")}])
                            st.session_state["activity_feed"] = pd.concat([new_act, st.session_state["activity_feed"]], ignore_index=True)
                            
                            # Add to Talent Management if Hired
                            if next_stage == "Hired":
                                roles_df = st.session_state.get("roles_df", pd.DataFrame())
                                role_match = roles_df[roles_df["Role"] == row["Role"]]
                                dept = role_match.iloc[0]["Department"] if not role_match.empty and "Department" in role_match.columns else "General"
                                
                                new_emp = pd.DataFrame([{
                                    "Employee": row["Name"], "Department": dept, "Role": row["Role"], 
                                    "Tenure (yrs)": 0.0, "Risk Score": 10, "Risk Level": "Low", "Engagement Score": 100, 
                                    "Python": 50, "Cloud": 50, "Communication": 50, "Data Analysis": 50, "Leadership": 50
                                }])
                                st.session_state["employees_df"] = pd.concat([new_emp, st.session_state["employees_df"]], ignore_index=True)
                                
                                new_onb = pd.DataFrame([{
                                    "Name": row["Name"], "Role": row["Role"], "Progress": 10, "Tasks Completed": "Offer accepted"
                                }])
                                st.session_state["onboarding_df"] = pd.concat([new_onb, st.session_state["onboarding_df"]], ignore_index=True)
                                
                            st.rerun()
                            
                        if c2.button("Reject", key=f"r_{row['Name']}_{stage}", help="Reject candidate", use_container_width=True):
                            idx = df[df["Name"] == row["Name"]].index[0]
                            st.session_state["candidates_df"].at[idx, "Stage"] = "Rejected"
                            new_act = pd.DataFrame([{"Activity": f"Rejected {row['Name']} from {stage}", "Time": datetime.now().strftime("%I:%M %p")}])
                            st.session_state["activity_feed"] = pd.concat([new_act, st.session_state["activity_feed"]], ignore_index=True)
                            st.rerun()

def page_jd_generator():
    st.title("JD Generator")
    st.caption("Generate a role-specific job description.")

    c1, c2 = st.columns([1, 1.3])
    with c1:
        title = st.selectbox("Job Title", get_unique_roles())
        dept = st.selectbox("Department", get_unique_departments())
        level = st.select_slider("Experience Level", ["Intern", "Junior", "Mid", "Senior", "Lead"], value="Mid")
        location = st.text_input("Location", "Remote / Bengaluru, India")
        skills_str = st.text_input("Key Skills (comma separated)", "Python, PyTorch, MLOps")
        gen = st.button("Generate JD")

    with c2:
        if gen:
            prompt = (
                f"Write a professional job description.\nTitle: {title}\nDept: {dept}\nLevel: {level}\nLoc: {location}\nSkills: {skills_str}\n"
                "Format in Markdown with ### headers: 'About the Role', 'What You'll Do', 'Must-Have Skills', 'Nice to Have'."
            )
            with st.spinner("Drafting with Llama 3.2..."):
                jd_text, err = call_llama([{"role": "user", "content": prompt}], temperature=0.5)
            if err: st.error(err)
            else: st.session_state["jd_text"] = jd_text

    if "jd_text" in st.session_state:
        st.markdown(st.session_state["jd_text"])

def page_interview_questions():
    st.title("Interview Question Generator")
    c1, c2, c3 = st.columns(3)
    with c1: role = st.selectbox("Role", get_unique_roles())
    with c2: difficulty = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"], value="Medium")
    with c3: categories = st.multiselect("Categories", ["Technical", "Behavioral", "Role-Specific"], default=["Technical"])

    if st.button("Generate Questions"):
        prompt = f"Generate interview questions for a {role} at {difficulty} level. Categories: {', '.join(categories)}."
        with st.spinner("Generating questions..."):
            questions_text, err = call_llama([{"role": "user", "content": prompt}], temperature=0.6)
        if err: st.error(err)
        else: st.session_state["questions_text"] = questions_text
    if "questions_text" in st.session_state: st.markdown(st.session_state["questions_text"])

def page_hr_assistant():
    st.title("HR Assistant")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "text": "Hi! Ask me about open roles or HR policy."}]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.write(msg["text"])

    user_input = st.chat_input("Ask the HR Assistant...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "text": user_input})
        with st.chat_message("user"): st.write(user_input)
        
        # Inject dynamic context into the system prompt
        roles_ctx = st.session_state.get("roles_df", pd.DataFrame()).to_csv(index=False)
        cands_ctx = st.session_state.get("candidates_df", pd.DataFrame()).to_csv(index=False)
        emps_ctx = st.session_state.get("employees_df", pd.DataFrame()).to_csv(index=False)
        
        system_prompt = (
            "You are a strict, helpful, and concise HR assistant. You only have access to the company's real-time data. "
            "Use the following CSV data to accurately answer the user's questions about roles, candidates, or employees.\n\n"
            f"OPEN ROLES:\n{roles_ctx}\n\n"
            f"CANDIDATES PIPELINE:\n{cands_ctx}\n\n"
            f"EMPLOYEES:\n{emps_ctx}\n\n"
            "CRITICAL RULE: You MUST ONLY answer questions related to the company, HR policies, or the provided CSV data. "
            "If the user asks ANYTHING else (general knowledge, coding, cooking, off-topic subjects), you must politely but firmly refuse to answer and redirect them back to HR topics."
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        for m in st.session_state.chat_history: messages.append({"role": m["role"], "content": m["text"]})
        with st.chat_message("assistant"):
            with st.spinner("Analyzing HR data..."):
                reply, err = call_llama(messages, temperature=0.3)
            if err: reply = f"⚠️ {err}"
            st.write(reply)
        st.session_state.chat_history.append({"role": "assistant", "text": reply})

def page_jd_analyzer():
    st.title("JD Analyzer")
    st.caption("Extract structured requirements from Job Descriptions.")
    
    jd_input = st.text_area("Paste Job Description Here", height=200, placeholder="We are looking for a Senior Data Scientist...")
    
    if st.button("Analyze JD", type="primary"):
        if jd_input.strip():
            with st.spinner("Analyzing Job Description..."):
                prompt = (
                    "You are an expert recruiter AI. Analyze the following Job Description and extract the key requirements in strictly valid JSON format. "
                    "Do not include any markdown formatting, backticks, or comments. Output ONLY the raw JSON object.\n\n"
                    "Schema:\n"
                    "{\n"
                    "  \"job_title\": \"string\",\n"
                    "  \"experience_level\": \"string (e.g., Junior, Mid, Senior)\",\n"
                    "  \"required_skills\": [\"skill1\", \"skill2\"],\n"
                    "  \"qualifications\": [\"qual1\", \"qual2\"]\n"
                    "}\n\n"
                    f"Job Description:\n{jd_input}"
                )
                response, err = call_llama([{"role": "user", "content": prompt}], temperature=0.1)
                
                if err:
                    st.error(err)
                else:
                    try:
                        # Clean up response in case it contains markdown block
                        if response.startswith("```json"):
                            response = response[7:]
                        if response.startswith("```"):
                            response = response[3:]
                        if response.endswith("```"):
                            response = response[:-3]
                            
                        parsed = json.loads(response.strip())
                        st.session_state["analyzed_jd"] = parsed
                        st.success("Analysis Complete!")
                    except json.JSONDecodeError:
                        st.error("Failed to parse the LLM output as JSON. Please try again.")
                        st.text(response)
        else:
            st.warning("Please paste a job description first.")
            
    if "analyzed_jd" in st.session_state:
        jd = st.session_state["analyzed_jd"]
        st.subheader(f"Analyzed Role: {jd.get('job_title', 'Unknown')}")
        c1, c2 = st.columns(2)
        c1.metric("Experience Level", jd.get('experience_level', 'Not specified'))
        
        st.write("**Required Skills**")
        skills = jd.get('required_skills', [])
        if skills:
            st.write(", ".join([f"`{s}`" for s in skills]))
        else:
            st.write("None extracted.")
            
        st.write("**Qualifications**")
        for q in jd.get('qualifications', []):
            st.write(f"- {q}")

def page_candidate_ranking():
    st.title("Candidate Matching & Ranking")
    st.caption("View candidates ranked by their AI match scores.")
    
    candidates = get_candidates()
    if candidates.empty or "AI Match %" not in candidates.columns:
        st.info("No candidates available for ranking.")
        return

    roles = candidates["Role"].dropna().unique().tolist()
    if not roles:
        roles = ["All Roles"]
    else:
        roles = ["All Roles"] + roles
        
    selected_role = st.selectbox("Filter by Role", roles)
    
    if selected_role != "All Roles":
        filtered_cands = candidates[candidates["Role"] == selected_role]
    else:
        filtered_cands = candidates
        
    if filtered_cands.empty:
        st.info(f"No candidates found for {selected_role}.")
        return
        
    filtered_cands = filtered_cands.sort_values(by="AI Match %", ascending=False)
    
    st.subheader("🏆 Leaderboard")
    for i, (_, row) in enumerate(filtered_cands.iterrows()):
        score = row.get("AI Match %", 0)
        color = "green" if score >= 80 else "orange" if score >= 60 else "red"
        
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                st.markdown(f"### #{i+1}")
                st.markdown(f"<h2 style='color:{color}'>{score}%</h2>", unsafe_allow_html=True)
            with c2:
                st.write(f"**{row.get('Name', 'Unknown')}**")
                st.caption(row.get("Role", "Unspecified"))
                st.write(f"Current Stage: {row.get('Stage', 'Unknown')}")
            with c3:
                if st.button("View Profile", key=f"view_{i}_{row.get('Name')}"):
                    st.info("Go to 'Resume Screening' to view detailed profile.")

def page_outreach_scheduling():
    st.title("Outreach & Scheduling")
    st.caption("Communicate with candidates and schedule interviews.")
    
    candidates = get_candidates()
    if candidates.empty:
        st.info("No candidates in the pipeline.")
        return
        
    cands_list = candidates["Name"].tolist()
    selected_name = st.selectbox("Select Candidate", cands_list)
    cand_data = candidates[candidates["Name"] == selected_name].iloc[0]
    cand_email = cand_data.get("Email", "candidate@example.com")
    
    tab1, tab2 = st.tabs(["AI Email Generator", "Meeting Scheduler"])
    
    with tab1:
        st.subheader("Draft Email")
        email_type = st.selectbox("Email Type", ["Interview Invite", "Offer Letter", "Rejection", "Custom Follow-up"])
        
        if st.button("Generate Draft", type="primary"):
            with st.spinner("Drafting email..."):
                prompt = (
                    f"Write a professional '{email_type}' email to {selected_name} for the {cand_data.get('Role', 'role')} position. "
                    "Make it warm and concise. Do not include placeholders for the sender name, just sign off as 'The Hiring Team'."
                )
                draft, err = call_llama([{"role": "user", "content": prompt}], temperature=0.7)
                if not err:
                    st.session_state["email_draft"] = draft
                else:
                    st.error(err)
                    
        draft_content = st.session_state.get("email_draft", "")
        edited_draft = st.text_area("Email Content", value=draft_content, height=300)
        
        if draft_content:
            import urllib.parse
            subject = f"Update regarding your application for {cand_data.get('Role', 'Role')}"
            
            subject_q = urllib.parse.quote(subject)
            body_q = urllib.parse.quote(edited_draft)
            gmail_link = f"https://mail.google.com/mail/?view=cm&fs=1&to={cand_email}&su={subject_q}&body={body_q}"
            
            if st.button("Send via Gmail API", type="primary"):
                from utils.google_auth import get_gmail_service
                service, err = get_gmail_service()
                
                if err:
                    st.warning(f"API Error: {err}")
                    st.info("💡 Place 'credentials.json' in the project folder to use the API directly.")
                    st.markdown(f'<a href="{gmail_link}" target="_blank"><button style="background-color:#6c5ce7;color:white;padding:10px 24px;border:none;border-radius:4px;cursor:pointer;">Send via Web Gmail instead</button></a>', unsafe_allow_html=True)
                else:
                    try:
                        import base64
                        from email.message import EmailMessage
                        
                        message = EmailMessage()
                        message.set_content(edited_draft)
                        message['To'] = cand_email
                        message['From'] = 'me'
                        message['Subject'] = subject

                        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
                        create_message = {'raw': encoded_message}
                        
                        with st.spinner("Sending email..."):
                            send_message = service.users().messages().send(userId="me", body=create_message).execute()
                            
                        new_act = pd.DataFrame([{"Activity": f"Sent {email_type} email to {selected_name} via Gmail API", "Time": datetime.now().strftime("%I:%M %p")}])
                        st.session_state["activity_feed"] = pd.concat([new_act, st.session_state["activity_feed"]], ignore_index=True)
                        st.success(f"Email sent successfully! Message ID: {send_message['id']}")
                        st.session_state["email_draft"] = ""
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
            
    with tab2:
        st.subheader("Schedule Interview")
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date")
            time = st.time_input("Time")
        with col2:
            duration = st.selectbox("Duration", ["30 mins", "45 mins", "60 mins", "90 mins"])
            format_type = st.selectbox("Format", ["Video Call", "Phone Call", "On-site"])
            
        interviewer = st.text_input("Interviewer Name", placeholder="e.g. Sarah Connor")
        
        if st.button("Generate Calendar Invite & Meet Link", type="primary"):
            df = st.session_state["candidates_df"]
            idx = df[df["Name"] == selected_name].index[0]
            if df.at[idx, "Stage"] in ["Applied", "Screening"]:
                df.at[idx, "Stage"] = "Interview"
                st.session_state["candidates_df"] = df
                
            act_text = f"Scheduled {format_type} with {selected_name} on {date} at {time}"
            new_act = pd.DataFrame([{"Activity": act_text, "Time": datetime.now().strftime("%I:%M %p")}])
            st.session_state["activity_feed"] = pd.concat([new_act, st.session_state["activity_feed"]], ignore_index=True)
            
            from utils.google_auth import get_calendar_service
            service, err = get_calendar_service()
            
            from datetime import timedelta
            dt_start = datetime.combine(date, time)
            duration_mins = int(duration.split()[0])
            dt_end = dt_start + timedelta(minutes=duration_mins)
            
            if err:
                st.warning(f"API Error: {err}")
                st.info("💡 Place 'credentials.json' in the project folder to use the API directly.")
                
                # Fallback to web link
                import urllib.parse
                title = urllib.parse.quote(f"Interview: {selected_name} & {interviewer} - {cand_data.get('Role', 'Role')}")
                start_str = dt_start.strftime("%Y%m%dT%H%M%S")
                end_str = dt_end.strftime("%Y%m%dT%H%M%S")
                details = urllib.parse.quote(f"Interview with {selected_name} for the {cand_data.get('Role')} position. Interviewer: {interviewer}.")
                cal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&dates={start_str}/{end_str}&details={details}"
                
                if format_type == "Video Call":
                    st.info("💡 To generate a Google Meet link, click 'Add Google Meet video conferencing' on the Google Calendar page.")
                
                st.markdown(f'<a href="{cal_url}" target="_blank"><button style="background-color:#4285f4;color:white;padding:10px 24px;border:none;border-radius:4px;cursor:pointer;">Open in Google Calendar Web</button></a>', unsafe_allow_html=True)
            else:
                try:
                    local_tz = datetime.now().astimezone().tzinfo
                    start_iso = dt_start.replace(tzinfo=local_tz).isoformat()
                    end_iso = dt_end.replace(tzinfo=local_tz).isoformat()
                    
                    event = {
                      'summary': f"Interview: {selected_name} & {interviewer} - {cand_data.get('Role', 'Role')}",
                      'description': f"Interview with {selected_name} for the {cand_data.get('Role')} position. Interviewer: {interviewer}.",
                      'start': {
                        'dateTime': start_iso,
                      },
                      'end': {
                        'dateTime': end_iso,
                      },
                      'attendees': [
                        {'email': cand_email},
                      ],
                    }
                    
                    if format_type == "Video Call":
                        event['conferenceData'] = {
                            'createRequest': {
                                'requestId': f"hirelens_{datetime.now().timestamp()}",
                                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                            }
                        }

                    with st.spinner("Creating Calendar Event..."):
                        created_event = service.events().insert(
                            calendarId='primary', 
                            body=event,
                            conferenceDataVersion=1,
                            sendUpdates='all'
                        ).execute()
                    
                    st.success(f"Meeting logged and Calendar event created via API!")
                    
                    html_link = created_event.get('htmlLink')
                    st.markdown(f"[View Event in Google Calendar]({html_link})")
                    
                    if format_type == "Video Call":
                        meet_link = created_event.get('hangoutLink')
                        if meet_link:
                            st.info(f"🎥 **Google Meet Link:** [Join Meeting]({meet_link})")
                            
                except Exception as e:
                    st.error(f"An error occurred while creating the calendar event: {e}")
