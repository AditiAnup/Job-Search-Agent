import os
import asyncio
from typing import List, Dict
from dataclasses import dataclass
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from openai import OpenAI
import re


# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
firecrawl = FirecrawlApp(api_key=FIRECRAWL_API_KEY)


# Dataclass for jobs structure
@dataclass
class JobPost:
    job_title: str
    company: str
    location: str
    experience: str
    compensation: str
    link: str
    description: str


# Function to scrape jobs using Firecrawl
async def scrape_jobs(job_title: str, location: str, skills: List[str], pages: int = 3) -> List[Dict]:
    formatted_job_title = job_title.replace(" ", "+")
    formatted_location = location.replace(" ", "+")
    all_urls = []

    for p in range(1, pages + 1):
        all_urls.append(f"https://www.ziprecruiter.com/candidate/search?search={formatted_job_title}&location={formatted_location}&page={p}")
        all_urls.append(f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={formatted_job_title}&locT=C&locKeyword={formatted_location}&p={p}")
        all_urls.append(f"https://www.wayup.com/s/jobs/?title={formatted_job_title}&location={formatted_location}&page={p}")
        all_urls.append(f"https://joinhandshake.com/students/jobs/?q={formatted_job_title}&location={formatted_location}&page={p}")

    job_posts = []
    chunk_size = 10
    for i in range(0, len(all_urls), chunk_size):
        urls_chunk = all_urls[i:i+chunk_size]
        print(f"Scraping chunk {i//chunk_size + 1} with {len(urls_chunk)} URLs")

        raw_response = firecrawl.extract(
            urls=urls_chunk,
            prompt="""
            Extract job postings. Fields:
            - job_title
            - company
            - location
            - experience (years required, if any; else 'N/A')
            - compensation (salary/hourly range if listed, else 'N/A')
            - link
            - description (FULL job description if available; if missing, summarize responsibilities and requirements from listing)
            Return as JSON under 'job_postings'.
            """,
            schema={
                "type": "object",
                "properties": {
                    "job_postings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "job_title": {"type": "string"},
                                "company": {"type": "string"},
                                "location": {"type": "string"},
                                "experience": {"type": "string"},
                                "compensation": {"type": "string"},
                                "link": {"type": "string"},
                                "description": {"type": "string"},
                            },
                            "required": ["job_title", "company", "location", "link"],
                        },
                    }
                },
                "required": ["job_postings"],
            },
            enable_web_search=False,
            ignore_invalid_urls=True,
        )

        data = getattr(raw_response, "data", None)
        if data:
            job_posts.extend(data.get("job_postings", []))

    print(f"✅ Raw Jobs Extracted: {len(job_posts)}")
    return job_posts


# Display the jobs
def display_jobs(jobs: List[Dict], limit: int = 30):
    """Prints first N jobs in a clean format."""
    print(f"\n📋 Showing first {limit} jobs:\n")
    for i, job in enumerate(jobs[:limit], start=1):
        print(f"{i}. **{job.get('job_title')}** at {job.get('company')}")
        print(f"   📍 {job.get('location')}")
        print(f"   💰 Compensation: {job.get('compensation', 'N/A')}")
        print(f"   🔗 {job.get('link')}\n")


# AI Analysis Function
FEEDBACK_FILE = "agent_feedback.txt"

async def analyze_jobs(jobs, job_title, location, experience_years, skills):
    if not jobs or len(jobs) == 0:
        print("⚠️ No jobs found initially. Retrying scrape...")
        try:
            jobs = await scrape_jobs(job_title, location, skills, pages=2)
        except Exception as e:
            return f"❌ Failed to rerun job search: {e}"

        if not jobs:
            return "⚠️ Still no job listings found after retry. Try adjusting your search."


    feedback_memory = ""
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            feedback_memory = f.read().strip()

    memory_context = (
        f"\nUser Preferences from past feedback:\n{feedback_memory}\n"
        if feedback_memory else "\n(No prior feedback provided yet.)\n"
    )

    analysis_prompt = f"""
    You are an AI job analysis agent and career coach.

    {memory_context}

    Analyze the following job listings and tailor your insights
    according to the user's preferences and feedback memory.

    **Job Title to Match:** {job_title}
    **Preferred Location:** {location}
    **Experience Level:** {experience_years} years or less
    **Key Skills:** {", ".join(skills)}

    JOB DATA:
    {jobs}

    Please structure your analysis into clear sections:

    💼 **SELECTED JOB OPPORTUNITIES**
    • List 10 best-matching roles with title, company, and location.

    🔍 **SKILLS MATCH ANALYSIS**
    • Compare how well the user's skills align with job requirements.

    💡 **RECOMMENDATIONS**
    • Highlight top 3 roles based on the user's preferences and growth potential.
    • Indicate why each role stands out given the feedback memory.

    🧭 **NEXT STEPS**
    • Personalized advice on refining search or resume based on observed trends.
    • Suggest new skills or certifications aligned with their interests.
    """

    response = client.responses.create(
        model="gpt-4o",
        input=[{"role": "user", "content": analysis_prompt}],
        max_output_tokens=2000,
    )

    return response.output_text

def filter_jobs(jobs, job_title, skills, experience_years):
    results = []
    job_title_keywords = [w.lower() for w in job_title.split() if len(w) > 2]
    skills = [s.strip().lower() for s in skills if s.strip()]

    for job in jobs:
        title = (job.get("job_title") or "").lower()
        desc = (job.get("description") or "").lower()
        exp_text = (job.get("experience") or "").lower()

        title_score = sum(1 for k in job_title_keywords if k in title)

        skill_score = sum(1 for s in skills if s in desc)

        exp_ok = True
        exp_match = re.findall(r"(\d+)\+?\s*year", exp_text)
        if exp_match:
            required_years = int(exp_match[0])
            exp_ok = required_years <= (experience_years + 3) 

        results.append({
            **job,
            "title_score": title_score,
            "skill_score": skill_score,
            "exp_ok": exp_ok
        })

    results = sorted(
        results,
        key=lambda j: (j["title_score"], j["skill_score"], j["exp_ok"]),
        reverse=True
    )

    print(f"✅ After ranking: showing top {len(results)} of {len(jobs)} scraped jobs")
    return results




# Analyze selected job
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
    **Experience:** {job.get("experience", "N/A")}  
    **Compensation:** {job.get("compensation", "N/A")}  

    **Job Description:**  
    {jd_text}

    Please provide:

    🔑 **Key Skills & Technologies** the company is looking for  
    🏢 **About the Company** (size, reputation, domain, etc.)  
    📈 **Hiring Trends** (how many people hired recently, growth signals)  
    🌍 **Visa Sponsorship** (if any public data suggests this company sponsors visas)  
    💡 **Recommendations** for tailoring my resume to this role
    """

    response = client.responses.create(
        model="gpt-4o",
        input=[{"role": "user", "content": analysis_prompt}],
        max_output_tokens=1200,
    )

    return response.output_text
