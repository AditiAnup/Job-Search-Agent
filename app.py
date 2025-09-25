import asyncio
import streamlit as st
from jobScraper import scrape_jobs, analyze_jobs
from Nav_bar import Nav_bar

Nav_bar()

# Store the session state
if "jobs" not in st.session_state:
    st.session_state["jobs"] = []
if "selected_job" not in st.session_state:
    st.session_state["selected_job"] = None
if "analysis" not in st.session_state:
    st.session_state["analysis"] = ""

st.header("🔍 Job Search")

job_title = st.text_input("Job Title", "Software Engineer")
location = st.text_input("Location", "Austin, TX")
skills = st.text_area("Your Skills (comma separated)", "Python, Django, APIs, Cloud").split(",")
experience_years = st.number_input("Years of Experience", min_value=0, max_value=20, value=3)

if st.button("Search Jobs"):
    with st.spinner("Scraping job postings..."):
        st.session_state["jobs"] = asyncio.run(scrape_jobs(job_title, location, skills, pages=3))

    st.success(f"✅ Found {len(st.session_state['jobs'])} jobs.")

    with st.spinner("Analyzing jobs with AI..."):
        st.session_state["analysis"] = asyncio.run(
            analyze_jobs(st.session_state["jobs"], job_title, location, experience_years, skills)
        )

# Job selection tiles
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
