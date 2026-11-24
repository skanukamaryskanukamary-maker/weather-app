import re
import html

import streamlit as st
from pypdf import PdfReader

st.set_page_config(
    page_title="Resume Screening Tool",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #F4F7FB;
}
.block-container {
    max-width: 1100px;
    padding-top: 2rem;
}
.hero {
    background: linear-gradient(120deg, #17324D, #2878E5);
    padding: 28px 32px;
    border-radius: 16px;
    color: white;
    margin-bottom: 22px;
}
.hero h1 {
    color: white;
    margin: 0;
}
.hero p {
    color: #E5EEF9;
    margin: 8px 0 0;
}
.result-card {
    background: white;
    border: 1px solid #DCE5EF;
    border-left: 5px solid #2878E5;
    border-radius: 12px;
    padding: 18px 20px;
    margin: 12px 0;
    box-shadow: 0 3px 12px rgba(23, 50, 77, 0.07);
}
.resume-name {
    color: #17324D;
    font-size: 18px;
    font-weight: 700;
    overflow-wrap: anywhere;
}
.keyword-text {
    color: #34495E;
    font-size: 14px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>📄 Resume Screening Tool</h1>
    <p>Compare resumes with a job description using keyword matching.</p>
</div>
""", unsafe_allow_html=True)

job_description = st.text_area(
    "Paste the job description",
    height=180,
    placeholder="Paste the role requirements and skills here..."
)

uploaded_files = st.file_uploader(
    "Upload resumes in PDF format",
    type=["pdf"],
    accept_multiple_files=True
)


def extract_text(pdf_file):
    reader = PdfReader(pdf_file)
    pages = [page.extract_text() or "" for page in reader.pages]
    return " ".join(pages)


def get_keywords(text):
    words = re.findall(r"[a-zA-Z][a-zA-Z+#.]*", text.lower())
    common_words = {
        "the", "and", "for", "with", "you", "your", "are",
        "this", "that", "from", "will", "our", "have", "has"
    }
    return {
        word for word in words
        if word not in common_words and len(word) > 2
    }


if st.button("🔎 Screen resumes", type="primary", use_container_width=True):
    if not job_description.strip():
        st.warning("Please enter a job description.")
    elif not uploaded_files:
        st.warning("Please upload at least one PDF resume.")
    else:
        job_keywords = get_keywords(job_description)
        results = []

        for file in uploaded_files:
            try:
                resume_text = extract_text(file)
                resume_keywords = get_keywords(resume_text)
                matched = job_keywords & resume_keywords

                score = (
                    round(len(matched) / len(job_keywords) * 100)
                    if job_keywords else 0
                )

                results.append({
                    "Resume": file.name,
                    "Match Score": score,
                    "Matched Keywords": ", ".join(sorted(matched)) or "None"
                })
            except Exception as error:
                st.error(f"Could not read {file.name}: {error}")

        results.sort(
            key=lambda item: item["Match Score"],
            reverse=True
        )

        if results:
            st.markdown("## Screening Results")
            st.caption(
                "Resumes are ranked by keyword match with the job description."
            )

            average_score = round(
                sum(item["Match Score"] for item in results) / len(results)
            )
            top_score = results[0]["Match Score"]

            col1, col2, col3 = st.columns(3)
            col1.metric("Resumes Reviewed", len(results))
            col2.metric("Top Match", f"{top_score}%")
            col3.metric("Average Match", f"{average_score}%")

            st.write("")

            for rank, item in enumerate(results, start=1):
                score = item["Match Score"]

                if score >= 70:
                    color = "#16845B"
                    status = "Strong keyword match"
                elif score >= 40:
                    color = "#C17A00"
                    status = "Partial keyword match"
                else:
                    color = "#64748B"
                    status = "Limited keyword match"

                safe_name = html.escape(item["Resume"])
                safe_keywords = html.escape(item["Matched Keywords"])

                if len(safe_keywords) > 180:
                    safe_keywords = safe_keywords[:180] + "…"

                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="resume-name">
                            {rank}. {safe_name}
                        </div>
                        <div style="margin-top: 8px; color: #66788A;">
                            <span style="color: {color}; font-weight: 700;">
                                {score}% match
                            </span>
                            &nbsp;·&nbsp; {status}
                        </div>
                        <div class="keyword-text">
                            <b>Matched keywords:</b> {safe_keywords}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.info(
                "The score measures keyword overlap only. "
                "Please review each resume manually."
            )