import streamlit as st
import asyncio
from openai import OpenAI
import os
from dotenv import load_dotenv
from Nav_bar import Nav_bar

Nav_bar()

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


# Analysis function (selected job)
async def analyze_single_job(job: dict, skills: list) -> str:
    if not job:
        return "⚠️ No job selected."

    jd_text = job.get("description", "No description available.")
    company = job.get("company", "Unknown company")
    job_title = job.get("job_title", "Unknown role")

    analysis_prompt = f"""
    You are a career coach and research assistant.

    Analyze the following job:

    **Job Title:** {job_title}  
    **Company:** {company}  
    **Location:** {job.get("location", "N/A")}  
    **Experience Required:** {job.get("experience", "N/A")}  
    **Compensation:** {job.get("compensation", "N/A")}  

    **Job Description:**  
    {jd_text}

    Please provide:

    🔑 **Key Skills & Technologies** the company is looking for  
    🏢 **About the Company** (size, reputation, domain, etc.)  
    📈 **Hiring Trends** (recent growth, how many people hired recently, signals of expansion)  
    🌍 **Visa Sponsorship** (if any public data or hints suggest sponsorship opportunities)  
    💡 **Recommendations** for tailoring my resume to this role
    """

    response = client.responses.create(
        model="gpt-4o",
        input=[{"role": "user", "content": analysis_prompt}],
        max_output_tokens=1200,
    )

    return response.output_text


# Streamlit UI
st.header("📊 Job Analysis")

# Check if jobs exist
if "jobs" not in st.session_state or not st.session_state["jobs"]:
    st.warning("⚠️ No jobs available. Please run a search on the **Job Search** page first.")
else:
    jobs = st.session_state["jobs"]

    # Pick up search context
    job_title = st.session_state.get("job_title", "Role")
    skills = st.session_state.get("skills", [])
    experience_years = st.session_state.get("experience_years", 0)

    # Let user pick a job from the first 30
    job_options = [
        f"{i+1}. {job.get('job_title', 'N/A')} at {job.get('company', 'Unknown')} ({job.get('location', 'N/A')})"
        for i, job in enumerate(jobs[:30])
    ]

    selected_idx = st.selectbox(
        "Select a job for detailed analysis",
        range(len(job_options)),
        format_func=lambda x: job_options[x],
    )

    selected_job = jobs[selected_idx]

    st.subheader("📌 Selected Job")
    st.markdown(f"""
    **{selected_job.get('job_title', 'N/A')}**  
    🏢 {selected_job.get('company', 'Unknown')}  
    📍 {selected_job.get('location', 'N/A')}  
    💰 {selected_job.get('compensation', 'N/A')}  
    🔗 [Job Link]({selected_job.get('link', '#')})
    """)

    # Analysis button
    if st.button("🔎 Analyze This Job"):
        with st.spinner("Analyzing job details..."):
            analysis = asyncio.run(analyze_single_job(selected_job, skills))

        st.subheader("📄 Final Job Analysis")
        st.markdown(analysis)
