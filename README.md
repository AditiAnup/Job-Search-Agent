# Job Search Agent

Automated job scraping, AI-based job matching, resume tailoring, and feedback-driven refinement.

## Project Overview

This AI-powered job search and resume optimization tool automates the process of finding relevant job opportunities and tailoring a resume with minimal user effort. Instead of manually browsing job boards, copying descriptions, or rewriting resumes for every position, the system handles everything end-to-end using intelligent automation.
It scrapes jobs from multiple platforms, filters them based on user-defined skills, years of experience, and role preferences, and generates AI-driven insights about each position. Users can then select any role, upload their resume, and receive a tailored optimization based on the job description.
In short, this project serves as a personal AI job search assistant that identifies, analyzes, and helps you apply for the right jobs - faster and smarter.

## Features

1. Multi-site job scraping (ZipRecruiter, Glassdoor, Handshake, etc.)
2. Smart filtering based on skills, years of experience, and title
3. GPT-powered Job analysis
4. Resume upload and AI Optimization
5. Database Integration
6. Streamlit UI with job selection tiles.

## Tech Stack

- Python
- OpenAI GPT-4o
- Firecrawl API
- SQLite

## Project Structure
```
.
|-- app.py
|-- jobScraper.py
|-- resume_opt.py
|-- pages/
|  |-- Job_analysis.py
|  |-- selected_job.py
|-- database.py
|-- requirements.txt
|-- README.md
```

## Installation & Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Job-Search-Agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPEN_API_KEY=your_openai_api_key
   FIRECRAWL_API_KEY=your_firecrawl_key
   ```
4. **Run the app**
   ```bash
   streamlit run app.py
   ```
## How to use
1. Enter job role, location, years of experience, and skills
2. The code will scrape the job sites, and you'll see the top 30 results
3. You can analyze each job individually
4. Select a job on the first page, and then you can upload a resume and get the optimization suggestions on the resume optimization page.

## Future Improvements
1. Agent Feedback loop
2. Add ATS resume scoring
3. Scrape LinkedIn for job openings
