import asyncio
import streamlit as st
from jobScraper import scrape_jobs, display_jobs, analyze_jobs, filter_jobs
from Nav_bar import Nav_bar
from database import init_db, save_jobs_to_db

Nav_bar()

init_db()
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
        raw_jobs = asyncio.run(scrape_jobs(job_title, location, skills, pages=3))

    # Filter
    filtered_jobs = filter_jobs(raw_jobs, job_title, skills, experience_years)
    save_jobs_to_db(filtered_jobs)
    st.session_state["jobs"] = filtered_jobs

    st.success(f"✅ Found {len(filtered_jobs)} filtered jobs.")
    display_jobs(filtered_jobs, limit=30)

    with st.spinner("Analyzing jobs with AI..."):
        final_analysis = asyncio.run(analyze_jobs(filtered_jobs, job_title, location, experience_years, skills))

    st.subheader("📄 Final Job Analysis")
    st.markdown(final_analysis)


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
