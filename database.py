import sqlite3

def init_db(db_path="jobs.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT,
        company TEXT,
        location TEXT,
        experience TEXT,
        compensation TEXT,
        link TEXT UNIQUE,
        description TEXT,
        title_score INTEGER,
        skill_score INTEGER,
        exp_ok BOOLEAN,
        status TEXT DEFAULT 'Not Applied'   -- for tracking applications later
    )
    """)
    conn.commit()
    conn.close()


def save_jobs_to_db(jobs, db_path="jobs.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for job in jobs:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO jobs 
                (job_title, company, location, experience, compensation, link, description, title_score, skill_score, exp_ok)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.get("job_title"),
                job.get("company"),
                job.get("location"),
                job.get("experience"),
                job.get("compensation"),
                job.get("link"),
                job.get("description"),
                job.get("title_score", 0),
                job.get("skill_score", 0),
                int(job.get("exp_ok", True)),
            ))
        except Exception as e:
            print(f"⚠️ Skipped job: {e}")

    conn.commit()
    conn.close()


def load_jobs_from_db(limit=30, db_path="jobs.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT job_title, company, location, experience, compensation, link, description, status 
        FROM jobs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()

    jobs = [
        {
            "job_title": r[0],
            "company": r[1],
            "location": r[2],
            "experience": r[3],
            "compensation": r[4],
            "link": r[5],
            "description": r[6],
            "status": r[7],
        }
        for r in rows
    ]
    return jobs
