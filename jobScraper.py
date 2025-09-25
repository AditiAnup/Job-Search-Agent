import os
import asyncio
from typing import List, Dict
from dataclasses import dataclass
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from openai import OpenAI


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
async def analyze_jobs(jobs: List[Dict], job_title: str, location: str, experience_years: int, skills: List[str]) -> str:
    """Analyzes and ranks job postings using OpenAI GPT."""
    if not jobs:
        return "⚠️ No job listings found. Try adjusting your search."

    analysis_prompt = f"""
    You are a career coach. Analyze these job opportunities:

    {jobs}

    Filter for:
    - Title related to {job_title}
    - Location near {location}
    - Experience <= {experience_years} years
    - Skills: {", ".join(skills)}

    Provide your response in sections:

    💼 SELECTED JOB OPPORTUNITIES
    • List 10 best matching jobs with Job Title, Company, Location, Experience, Compensation

    🔍 SKILLS MATCH ANALYSIS
    • Compare jobs on skills match, experience, and growth potential

    💡 RECOMMENDATIONS
    • Top 3 jobs with reasoning
    • Career growth potential

    📝 APPLICATION TIPS
    • Resume customization tips
    • Application strategies
    """

    response = client.responses.create(
        model="gpt-4o",
        input=[{"role": "user", "content": analysis_prompt}],
        max_output_tokens=2000,
    )

    return response.output_text

# Analyze selected job
async def analyze_single_job(job: Dict) -> str:
    """
    Analyze a single job posting in detail.
    Summarize skills, company info, hiring trends, and visa sponsorship.
    """
    job_title = job.get("job_title", "")
    company = job.get("company", "")
    location = job.get("location", "")
    description = job.get("description", "")

    analysis_prompt = f"""
    You are an expert career analyst. A candidate is considering a job.

    --- JOB POSTING ---
    Title: {job_title}
    Company: {company}
    Location: {location}
    Description: {description}

    Provide the following structured response:

    🏢 COMPANY SNAPSHOT
    • Brief summary of what this company does, its industry, and reputation.

    📊 HIRING TRENDS
    • Has the company been hiring or laying off recently?
    • Approximate number of hires in the past few months (if known).

    🌍 VISA SPONSORSHIP
    • Does this company sponsor H-1B or OPT visas?
    • Any history of international hires?

    🛠️ SKILLS & REQUIREMENTS
    • Key skills this job is looking for
    • Experience levels required

    💡 TAKEAWAY
    • Is this role worth applying to?
    """

    response = client.responses.create(
        model="gpt-4o",
        input=[{"role": "user", "content": analysis_prompt}],
        max_output_tokens=1200,
    )

    return response.output_text
