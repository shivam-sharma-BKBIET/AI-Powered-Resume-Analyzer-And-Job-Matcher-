import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
from fuzzywuzzy import fuzz
import matplotlib.pyplot as plt
from wordcloud import WordCloud


def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_skills(resume_text, skill_set):
    resume_text = resume_text.lower()
    extracted = [skill for skill in skill_set if skill.lower() in resume_text]
    return extracted

def match_jobs(candidate_skills, jobs_df):
    matches = []
    for _, row in jobs_df.iterrows():
        job_skills = row["Skills"].split(", ")
        match_score = fuzz.token_set_ratio(candidate_skills, job_skills)
        matches.append((row["Job Title"], match_score, job_skills))
    sorted_matches = sorted(matches, key=lambda x: x[1], reverse=True)
    return sorted_matches[:3]

def generate_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
    return wordcloud


st.set_page_config(page_title="AI Resume Analyzer", layout="centered")
st.title(" AI-Powered Resume Analyzer & Job Matcher")

uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

if uploaded_file:
    resume_text = extract_text_from_pdf(uploaded_file)
    st.subheader("Resume Text Preview")
    st.text_area("", resume_text[:1000] + "...", height=200)

    
    skill_db = ["Python", "Java", "Machine Learning", "Deep Learning", "SQL", "Data Analysis",
                "Communication", "Leadership", "C++", "AWS", "Excel"]

    candidate_skills = extract_skills(resume_text, skill_db)
    st.subheader(" Extracted Skills")
    st.write(candidate_skills)

    
    data = {
        "Job Title": ["Data Scientist", "Software Engineer", "ML Engineer"],
        "Skills": ["Python, SQL, Machine Learning, Data Analysis",
                   "Java, C++, AWS, Communication",
                   "Python, Deep Learning, TensorFlow, Leadership"]
    }
    jobs_df = pd.DataFrame(data)

    st.subheader("🔍 Top Job Matches")
    top_matches = match_jobs(candidate_skills, jobs_df)
    for title, score, skills in top_matches:
        st.markdown(f"**{title}** - Match Score: `{score}%`")
        st.markdown(f"_Required Skills_: {', '.join(skills)}")
        missing = set(skills) - set(candidate_skills)
        if missing:
            st.warning(f"Missing Skills: {', '.join(missing)}")
        else:
            st.success("You match all required skills!")

    
    st.subheader("📊 Skill Match Visualization")
    labels = ['Matched Skills', 'Missing Skills']
    values = [len(candidate_skills), len(set(skill_db) - set(candidate_skills))]

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%')
    ax.axis('equal')
    st.pyplot(fig)

    st.subheader(" Resume Word Cloud")
    wc = generate_wordcloud(resume_text)
    st.image(wc.to_array(), use_column_width=True)
