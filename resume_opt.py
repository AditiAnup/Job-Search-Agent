import PyPDF2
import docx
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Extract Resume Text
def extract_resume_text(file_path: str) -> str:
    text = ""
    if file_path.endswith(".pdf"):
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        raise ValueError("Unsupported file format. Upload PDF, DOCX, or TXT.")
    return text.strip()

# Resume Optimization
def analyze_resume(resume_text: str, job_description: str) -> str:
    prompt = f"""
    You are a career coach. Compare the following resume to the job description. 

    Resume:
    {resume_text}

    Job Description:
    {job_description}

    Provide:
    1. 🔑 Missing Skills & Keywords
    2. 📝 Bullet Points to Add or Rephrase
    3. 💡 Overall Resume Improvement Suggestions
    """

    response = client.responses.create(
        model="gpt-4o",
        input=[{"role": "user", "content": prompt}],
        max_output_tokens=1200
    )

    return response.output_text
