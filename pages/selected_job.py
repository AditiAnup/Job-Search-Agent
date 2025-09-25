import tempfile
import streamlit as st
from resume_opt import extract_resume_text, analyze_resume
from Nav_bar import Nav_bar

Nav_bar()
st.header("📌 Resume Optimization")

if "selected_job" not in st.session_state or not st.session_state["selected_job"]:
    st.warning("⚠️ Please select a job on the main page first.")
else:
    job = st.session_state["selected_job"]
    st.subheader(f"Selected Job: {job['job_title']} at {job['company']}")
    st.write(f"📍 {job['location']}")
    st.write(f"💰 {job.get('compensation', 'N/A')}")
    st.write(f"[🔗 Job Link]({job.get('link')})")

    # Resume upload
    uploaded_resume = st.file_uploader("Upload Resume (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])

    if uploaded_resume and st.button("⚡ Optimize Resume"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_resume.name) as tmp:
            tmp.write(uploaded_resume.getbuffer())
            resume_path = tmp.name

        resume_text = extract_resume_text(resume_path)
        jd_text = job.get("description", "")

        if not jd_text:
            st.warning("⚠️ This job doesn't have a description available for comparison.")
        else:
            st.subheader("📌 Resume Optimization Results")

            # Call AI resume analyzer
            raw_analysis = analyze_resume(resume_text, jd_text)

            # ---- Formatting Trick ----
            st.markdown("### ✅ Matched Skills")
            st.info("These are the skills from your resume that match the job description (AI-detected).")
            st.write("• Placeholder for matched skills extracted from analysis")

            st.markdown("### ⚠️ Missing Skills")
            st.warning("These are the important skills from the job description missing in your resume.")
            st.write("• Placeholder for missing skills extracted from analysis")

            st.markdown("### 📈 Recommendations")
            st.success("Tailored suggestions to improve your resume for this job.")
            st.write("• Placeholder for AI-generated recommendations")

            # For debugging: show the full raw text at bottom (can hide later)
            with st.expander("🔎 Full AI Analysis"):
                st.markdown(raw_analysis)
