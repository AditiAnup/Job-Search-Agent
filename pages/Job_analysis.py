import streamlit as st
import asyncio
from jobScraper import analyze_single_job
from Nav_bar import Nav_bar

Nav_bar()
st.set_page_config(page_title="Job Analysis", layout="wide")
st.header("📊 Job Analysis")

# Ensure jobs exist in session state
if "jobs" not in st.session_state or not st.session_state["jobs"]:
    st.warning("⚠️ Run a job search first to load jobs.")
else:
    job_options = [
        f"{i+1}. {job['job_title']} at {job['company']} ({job['location']})"
        for i, job in enumerate(st.session_state["jobs"][:30])
    ]

    selected_job_idx = st.selectbox(
        "Pick a Job to Analyze",
        range(len(job_options)),
        format_func=lambda x: job_options[x]
    )

    if st.button("🔎 Analyze This Job"):
        with st.spinner("Analyzing job details..."):
            job = st.session_state["jobs"][selected_job_idx]
            detailed_analysis = asyncio.run(analyze_single_job(job))

        st.subheader("📌 Job Analysis Report")
        st.markdown(detailed_analysis)
