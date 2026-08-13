import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from utils.llm import call_llama
from utils.data_state import get_priority_roles, get_candidates

def page_talent_dashboard():
    st.title("Talent Dashboard")
    st.caption("High-level overview of employee health, skills, and engagement.")
    
    df = st.session_state["employees_df"]
    surveys = st.session_state["survey_df"]
    
    if df.empty:
        st.info("No employee data loaded.")
        return

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Employees", len(df))
    avg_risk = df["Risk Score"].mean() if "Risk Score" in df.columns else 0
    m2.metric("Avg Risk Score", f"{avg_risk:.1f}/100", delta="-2.1" if avg_risk < 50 else "+4.5", delta_color="inverse")
    
    engagement = surveys["Score"].iloc[-1] if not surveys.empty else 0
    prev_engagement = surveys["Score"].iloc[-2] if len(surveys) > 1 else engagement
    m3.metric("Overall Engagement", f"{engagement}%", delta=f"{engagement - prev_engagement}%")
    
    m4.metric("Avg Tenure", f"{df['Tenure (yrs)'].mean():.1f} yrs")
    
    st.divider()
    st.subheader("Department Health Breakdown")
    if "Department" in df.columns and "Engagement Score" in df.columns:
        dept_health = df.groupby("Department")[["Risk Score", "Engagement Score"]].mean().reset_index()
        fig = px.bar(dept_health, x="Department", y=["Engagement Score", "Risk Score"], barmode="group",
                     color_discrete_sequence=["#2ecc71", "#e74c3c"])
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.write("---")
    st.subheader("Candidate Analytics & Hiring Recommendations")
    
    roles, candidates = get_priority_roles(), get_candidates()
    open_reqs, total_cands = len(roles), len(candidates)
    
    r1, r2 = st.columns([1, 1.2])
    with r1:
        st.write("**Top Candidates by AI Match Score**")
        if not candidates.empty and "AI Match %" in candidates.columns:
            top_cands = candidates.sort_values(by="AI Match %", ascending=False).head(5)
            fig3 = px.bar(top_cands, x="AI Match %", y="Name", orientation="h", color="AI Match %", color_continuous_scale="Viridis", text="Role")
            fig3.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No candidates scored yet.")
            
    with r2:
        st.write("**Hiring Insights**")
        if not candidates.empty and "AI Match %" in candidates.columns:
            top_cand = candidates.sort_values(by="AI Match %", ascending=False).iloc[0]
            if top_cand["AI Match %"] > 85:
                st.success(f"🌟 **Fast-Track Recommended:** {top_cand['Name']} ({top_cand['Role']}) has an exceptional match score of {top_cand['AI Match %']}%. Proceed to offer phase quickly.")
            else:
                st.info(f"Top candidate {top_cand['Name']} scored {top_cand['AI Match %']}%. Continue sourcing for {top_cand['Role']}.")
                
            bottleneck = candidates["Stage"].value_counts().idxmax()
            if bottleneck in ["Screening", "Interview"]:
                st.warning(f"⚠️ **Bottleneck Alert:** You have a backlog of candidates in the '{bottleneck}' stage. Please review them.")
                
            if st.button("Generate Comprehensive Report"):
                with st.spinner("Generating Report..."):
                    prompt = f"Write a short recruitment performance report based on this data: Open Reqs: {open_reqs}, Candidates: {total_cands}, Pipeline Breakdown: {candidates['Stage'].value_counts().to_dict()}"
                    reply, err = call_llama([{"role": "user", "content": prompt}], temperature=0.3)
                    if not err:
                        st.info(reply)
                    else:
                        st.error(err)

def page_skills_ld():
    st.title("Skills & L&D Matrix")
    st.caption("Identify capability gaps via Radar chart and deploy dynamic training tracks.")
    
    df = st.session_state["employees_df"]
    if df.empty:
        st.info("No employee data available.")
        return

    role = st.selectbox("Select Role to Analyze", df["Role"].dropna().unique().tolist())
    categories = ["Python", "Cloud", "Communication", "Data Analysis", "Leadership"]
    
    # Calculate Team vs Ideal
    team_avg = df[df["Role"] == role][categories].mean().fillna(0).tolist()
    
    targets_df = st.session_state.get("skill_targets_df", pd.DataFrame())
    if not targets_df.empty and role in targets_df["Role"].values:
        ideal = targets_df[targets_df["Role"] == role][categories].iloc[0].fillna(0).tolist()
    else:
        ideal = [80, 80, 80, 80, 80] # Default baseline

    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=team_avg + [team_avg[0]], theta=categories + [categories[0]], fill='toself', name='Team Average', line_color='#3498db'))
        fig.add_trace(go.Scatterpolar(r=ideal + [ideal[0]], theta=categories + [categories[0]], fill='toself', name='Ideal Profile', line_color='#2ecc71'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, height=450, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Targeted L&D Recommendations")
        st.write(f"Based on the gaps for **{role}**:")
        gaps = {cat: ideal[i] - team_avg[i] for i, cat in enumerate(categories) if ideal[i] - team_avg[i] > 10}
        
        if not gaps:
            st.success("The team meets or exceeds all core skill requirements!")
        else:
            for skill, gap in sorted(gaps.items(), key=lambda x: -x[1]):
                with st.container(border=True):
                    st.write(f"**🚨 {skill} Gap ({gap:.1f} pts)**")
                    if skill == "Python": st.caption("Recommended: Advanced Python Architecture Bootcamp")
                    elif skill == "Cloud": st.caption("Recommended: AWS Certification Path")
                    else: st.caption(f"Recommended: {skill} Masterclass")
                    
                    if st.button(f"Assign {skill} Track", key=f"btn_{skill}_{role}"):
                        # Find all employees with this role and boost their skill
                        emp_indices = df[df["Role"] == role].index
                        for idx in emp_indices:
                            # Boost the specific skill by 15 points (up to max 100)
                            new_val = min(100, df.at[idx, skill] + 15)
                            df.at[idx, skill] = new_val
                        st.session_state["employees_df"] = df
                        
                        new_activity = pd.DataFrame([{"Activity": f"Assigned {skill} Track to the {role} team", "Time": datetime.now().strftime("%I:%M %p")}])
                        st.session_state["activity_feed"] = pd.concat([new_activity, st.session_state["activity_feed"]], ignore_index=True)
                        st.success(f"Track assigned! Check Activity Feed.")
                        st.rerun()

def page_attrition_engagement():
    st.title("Employee Health: Attrition & Engagement")
    st.caption("Pinpoint high-risk employees and take immediate action.")
    
    df = st.session_state["employees_df"]
    if df.empty or "Engagement Score" not in df.columns:
        st.info("Employee engagement and risk data not available.")
        return

    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        st.subheader("Risk vs Engagement Matrix")
        fig = px.scatter(df, x="Engagement Score", y="Risk Score", color="Risk Level", hover_name="Employee",
                         hover_data=["Role", "Tenure (yrs)"], size="Tenure (yrs)", 
                         color_discrete_map={"High": "red", "Medium": "orange", "Low": "green"})
        
        # Draw danger zone
        fig.add_shape(type="rect", x0=0, y0=70, x1=50, y1=100, fillcolor="red", opacity=0.1, line_width=0)
        fig.add_annotation(x=25, y=90, text="DANGER ZONE", showarrow=False, font=dict(color="red", size=14))
        
        fig.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Critical Interventions Required")
        high_risk = df[(df["Risk Score"] > 70) & (df["Engagement Score"] < 60)]
        if high_risk.empty:
            st.success("No employees currently in the critical danger zone.")
        else:
            for _, row in high_risk.iterrows():
                with st.container(border=True):
                    st.error(f"**{row['Employee']}**")
                    st.caption(f"{row['Role']} · {row['Tenure (yrs)']} yrs")
                    st.caption(f"Risk: {row['Risk Score']} | Engagement: {row['Engagement Score']}")
                    
                    if st.button("Schedule 1-on-1 Sync", key=f"sync_{row['Employee']}", use_container_width=True):
                        # Workable button: lowers risk, increases engagement, logs activity
                        emp_idx = df[df["Employee"] == row['Employee']].index
                        if not emp_idx.empty:
                            idx = emp_idx[0]
                            new_risk = max(0, df.at[idx, "Risk Score"] - 30)
                            new_engagement = min(100, df.at[idx, "Engagement Score"] + 25)
                            
                            df.at[idx, "Risk Score"] = new_risk
                            df.at[idx, "Engagement Score"] = new_engagement
                            df.at[idx, "Risk Level"] = "Low" if new_risk < 40 else "Medium" if new_risk < 70 else "High"
                            st.session_state["employees_df"] = df
                            
                            new_act = pd.DataFrame([{"Activity": f"Scheduled 1-on-1 with {row['Employee']}", "Time": datetime.now().strftime("%I:%M %p")}])
                            st.session_state["activity_feed"] = pd.concat([new_act, st.session_state["activity_feed"]], ignore_index=True)
                            
                            st.rerun()

def page_onboarding_tracker():
    st.title("Onboarding Timeline")
    st.caption("Track new-hire progress through critical onboarding milestones.")
    
    df = st.session_state["onboarding_df"]
    if df.empty:
        st.info("No active onboardings found.")
        return
        
    for _, row in df.iterrows():
        with st.container(border=True):
            pct = row.get("Progress", 0)
            name = row.get("Name", "Unknown")
            role = row.get("Role", "Role")
            
            st.subheader(f"👋 {name} — {role}")
            st.progress(int(pct) / 100)
            
            # Interactive checklist to advance onboarding progress
            col1, col2, col3, col4 = st.columns(4)
            
            def onboarding_step(col, label, threshold, current_pct, emp_name):
                with col:
                    if current_pct >= threshold:
                        st.markdown(f"✅ **{label}**")
                    else:
                        if st.button(f"Complete: {label}", key=f"btn_{threshold}_{emp_name}", use_container_width=True):
                            idx = df[df["Name"] == emp_name].index[0]
                            st.session_state["onboarding_df"].at[idx, "Progress"] = threshold
                            st.session_state["onboarding_df"].at[idx, "Tasks Completed"] = label
                            
                            new_act = pd.DataFrame([{"Activity": f"Completed onboarding step '{label}' for {emp_name}", "Time": datetime.now().strftime("%I:%M %p")}])
                            st.session_state["activity_feed"] = pd.concat([new_act, st.session_state["activity_feed"]], ignore_index=True)
                            st.rerun()

            onboarding_step(col1, "Offer Signed", 25, pct, name)
            onboarding_step(col2, "IT Setup", 50, pct, name)
            onboarding_step(col3, "Week 1 Sync", 75, pct, name)
            onboarding_step(col4, "30-Day Review", 100, pct, name)
