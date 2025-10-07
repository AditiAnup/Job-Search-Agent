import asyncio
import streamlit as st
from jobScraper import scrape_jobs, display_jobs, analyze_jobs, filter_jobs
from Nav_bar import Nav_bar
from database import init_db, save_jobs_to_db
import os

FEEDBACK_FILE = "agent_feedback.txt"

Nav_bar()
init_db()

# Helper functions for agent memory
def load_agent_feedback():
    """Read stored feedback memory."""
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def save_agent_feedback(feedback: str):
    """Append new feedback to agent memory."""
    feedback = feedback.strip()
    if feedback:
        with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{feedback}")
    st.success("✅ Feedback saved! Agent will remember this next time.")

def reset_agent_feedback():
    """Clear all saved feedback."""
    if os.path.exists(FEEDBACK_FILE):
        os.remove(FEEDBACK_FILE)
        st.success("🧹 Agent memory reset!")

# Session state setup
if "jobs" not in st.session_state:
    st.session_state["jobs"] = []
if "selected_job" not in st.session_state:
    st.session_state["selected_job"] = None
if "analysis" not in st.session_state:
    st.session_state["analysis"] = ""

# Job Search UI
st.header("🔍 Job Search")

job_title = st.text_input("Job Title", "Software Engineer")
location = st.text_input("Location", "Austin, TX")
skills = st.text_area("Your Skills (comma separated)", "Python, Django, APIs, Cloud").split(",")
experience_years = st.number_input("Years of Experience", min_value=0, max_value=20, value=3)

# Load memory context
agent_memory = load_agent_feedback()

if st.button("Search Jobs"):
    with st.spinner("Scraping job postings..."):
        raw_jobs = asyncio.run(scrape_jobs(job_title, location, skills, pages=3))

    # Filter jobs
    filtered_jobs = filter_jobs(raw_jobs, job_title, skills, experience_years)
    save_jobs_to_db(filtered_jobs)
    st.session_state["jobs"] = filtered_jobs

    st.success(f"✅ Found {len(filtered_jobs)} filtered jobs.")
    display_jobs(filtered_jobs, limit=30)

    # Combine feedback memory into AI analysis prompt
    st.info("🤖 Agent is considering your previous feedback...")
    combined_skills = skills + agent_memory.split(",") if agent_memory else skills

    with st.spinner("Analyzing jobs with AI..."):
        final_analysis = asyncio.run(
            analyze_jobs(filtered_jobs, job_title, location, experience_years, combined_skills)
        )

    st.subheader("📄 Final Job Analysis")
    st.markdown(final_analysis)

# Feedback section

st.divider()
st.subheader("Agent Feedback (Persistent Memory)")

with st.expander("🪄 View Agent Memory"):
    memory = load_agent_feedback()
    if memory:
        st.text_area("Agent's current memory:", memory, height=100, disabled=True)
    else:
        st.info("No feedback stored yet.")

feedback = st.text_input("Give feedback to improve future results (e.g., 'more remote roles', 'fewer senior jobs')")

col1, col2 = st.columns(2)
with col1:
    if st.button("💾 Save Feedback"):
        if feedback:
            save_agent_feedback(feedback)
        else:
            st.warning("Please type some feedback first.")
with col2:
    if st.button("🧹 Reset Agent Memory"):
        reset_agent_feedback()

# ----------------------------
# 📋 Job selection section
# ----------------------------
if st.session_state["jobs"]:
    st.subheader("📋 Select a Job for Resume Optimization")
    for i, job in enumerate(st.session_state["jobs"][:30]):
        with st.container(border=True):
            st.markdown(f"### {job['job_title']}")
            st.write(f"**Company:** {job['company']}")
            st.write(f"**Location:** {job['location']}")
            st.write(f"**Compensation:** {job.get('compensation', 'N/A')}")
            st.write(f"[🔗 Job Link]({job.get('link')})")

            if st.button(f"Select Job {i+1}", key=f"select_{i}"):
                st.session_state["selected_job"] = job
                st.success(f"✅ Selected: {job['job_title']} at {job['company']}")
