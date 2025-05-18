import os
import shutil
import streamlit as st
from services import ResumeParser
from gemini import evaluate_candidate,generate_interview_questions


SAVE_FOLDER_DIR = "resumes"
resume_upload_path = None

if os.path.exists(SAVE_FOLDER_DIR):
    shutil.rmtree(SAVE_FOLDER_DIR)
os.makedirs(SAVE_FOLDER_DIR)

st.set_page_config(
    page_title="Talent Sort", 
    layout="wide",
)

theme_choice = st.sidebar.selectbox("Choose Theme", ["Dark", "Light"])

if theme_choice == "Dark":
    bg_color = "#0E1117"
    text_color = "white"
    input_bg = "#262730"
else:
    bg_color = "white"
    text_color = "black"
    input_bg = "#f0f2f6"

# --- Custom Styles ---
st.markdown(f"""
<style>
.stApp {{
    background-color: {bg_color};
    color : {text_color};
}}
.stTextInput > label, .stFileUploader label, .stTextArea label {{
    font-weight: bold;
    color: {text_color};
}}
.stButton>button {{
    background-color: #1E88E5;
    color: white !important;
    font-weight: bold;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    justify-content: center;
    width: 50%;
    transition: background-color 0.3s ease;
}}
.stButton>button:hover {{
    background-color: #1565C0;
}}

/* Form Submit Button Fix */
button[kind="primary"] {{
    background-color: #1E88E5 !important;
    color: white !important;
    font-weight: bold;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    font-size: 16px;
    cursor: pointer;
    width: 100%;
    transition: background-color 0.3s ease;
}}
button[kind="primary"]:hover {{
    background-color: #1565C0 !important;
}}

h1 {{
    color: #1E88E5;
    text-align: center;
    margin-bottom: 20px;
}}
h2 {{
    margin-top: 20px;
    margin-bottom: 10px;
    border-bottom: 2px solid #1E88E5;
    padding-bottom: 5px;
}}
.stTextArea, .stFileUploader, .stTextInput {{
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #cccccc;
    background-color: {input_bg};
    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}}
</style>
""", unsafe_allow_html=True)


st.title('TalentSort')

with st.form("talent_evaluation_form"):

    col1, col2, col3 = st.columns(3)

    with col1:
        job_description_input = st.text_area(
            label="📜 Job Description",
            height=350, 
            help="Paste the full text of the job description here."
        )



    with col2:
        resume_input = st.file_uploader(
            label="📄 Upload Resume", 
            type=['pdf', 'doc', 'docx', 'txt'],
            help="Upload the candidate's resume file (PDF, Word, or TXT)."
        )
        if resume_input:
            resume_upload_path = os.path.join(SAVE_FOLDER_DIR,resume_input.name)
            with open(resume_upload_path, mode='wb') as f:
                f.write(resume_input.read())  

        suggest_ques = st.toggle(label= "Suggest interview questions", help="Switch it ON to get relevant interview questions and answers to assess the candidate's technical proficiency.")



    with col3:

        scoring_extra_prompt = st.text_area(
            label="Specific focus for evaluation (Optional):",
            height=120,
            value="", 
            placeholder="e.g., 'Prioritize cloud computing (AWS/Azure) experience', 'Emphasize leadership examples and project management skills', 'Assess Python proficiency'.",
            help="Provide any specific keywords, skills, or attributes to emphasize during the resume and JD matching."
        )

        interview_questions_extra_prompt = st.text_area(
            label="Guidelines for interview questions (Optional):",
            height=120,
            value="", 
            placeholder="e.g., 'Generate 10 technical questions based on resume', 'Create 3 technical questions about data structures in Python'",
            help="Specify the type, number, or focus areas for the interview questions you want to generate."
        )

       

    # --- Submit Button ---
    st.markdown("---") 
    col = st.columns(7)[3] 
    with col:
        submit_button = st.form_submit_button(label='Evaluate')


if submit_button:
    if job_description_input and resume_input:
        with st.spinner("Evaluating candidate talent..."):
            resume_text = ResumeParser.extract_text_from_resume(resume_upload_path)
            eval_output = evaluate_candidate(job_description=job_description_input,\
                               resume_str=resume_text,
                               additional_instruction=scoring_extra_prompt)
            
            if suggest_ques:
                # Generate interview questions
                interview_questions_answers = generate_interview_questions(
                    job_description_input, resume_text,additional_instruction=interview_questions_extra_prompt
                )
                # st.write(interview_questions_answers.parsed.questions_answers)
            
            st.markdown("---")
            st.subheader("🎯 Evaluation Results")

            score = eval_output.parsed.required_skills_score + eval_output.parsed.responsibilities_score + eval_output.parsed.overall_relevance_score 
            score_color_bg = "#333"
            score_text_color = "white"
            if score >= 80:
                score_color_bg = "#4CAF50" 
            elif score >= 60:
                score_color_bg = "#FF9800" 
            else:
                score_color_bg = "#F44336"
            
            st.markdown(f"""
            <div style="
                background-color: {score_color_bg}; 
                color: {score_text_color}; 
                padding: 20px; 
                border-radius: 10px; 
                text-align: center; 
                margin-bottom:10px;
            ">
                <p style="font-size: 20px; margin-bottom: 5px; font-weight: bold;">Candidate Compatibility Score</p>
                <p style="font-size: 40px; margin-bottom: 0; font-weight: bold;">{score} <span style="font-size: 24px;">/ 100</span></p>
            </div>
            """, unsafe_allow_html=True)
            st.progress(score / 100)
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("#### Detailed Feedback")

            with st.container(): 
                # feedback_text = f"**Introduction**  \n{eval_output.parsed.Introduction}  \n**Education  (Score - {eval_output.parsed.Education_score}/20)**  \n{eval_output.parsed.Education_feedback}  \n**Experience  (Score - {eval_output.parsed.Experience_score}/35)**  \n{eval_output.parsed.Experience_feedback}  \n**Required Skills  (Score - {eval_output.parsed.Required_Skills_score}/35)**  \n{eval_output.parsed.Required_Skills_feedback}  \n**Responsibilities  (Score - {eval_output.parsed.Responsibilities_score}/10)**  \n{eval_output.parsed.Responsibilities_feedback}  \n\n**Strengths**  \n{eval_output.parsed.Strengths}  \n**Areas of Concern/Gaps**  \n{eval_output.parsed.Concerns}"
                
                # Introduction
                st.markdown("### Introduction")
                st.markdown(f"{eval_output.parsed.evaluation_summary or 'No summary available.'}")

                # Educational Details
                st.markdown("### Educational Details")
                if eval_output.parsed.extracted_education:
                    for edu_item in eval_output.parsed.extracted_education:
                        st.markdown(f"- {edu_item}")
                else:
                    st.markdown("_No education details found._")

                # Experience Details
                st.markdown("### Experience Details")
                if eval_output.parsed.extracted_experience:
                    for exp_item in eval_output.parsed.extracted_experience:
                        st.markdown(f"- {exp_item}")
                else:
                    st.markdown("_No experience details found._")

                # Required Skills
                st.markdown(f"### Required Skills (Score: {eval_output.parsed.required_skills_score}/50)")
                st.markdown(f"{eval_output.parsed.required_skills_feedback or 'No feedback provided.'}")

                # Responsibilities
                st.markdown(f"### Responsibilities (Score: {eval_output.parsed.responsibilities_score}/40)")
                st.markdown(f"{eval_output.parsed.responsibilities_feedback or 'No feedback provided.'}")

                # Overall Profile Relevance
                st.markdown(f"### Overall Profile Relevance (Score: {eval_output.parsed.overall_relevance_score}/10)")
                st.markdown(f"{eval_output.parsed.overall_relevance_feedback or 'No feedback provided.'}")

                # Strengths
                st.markdown("### Strengths")
                st.markdown(f"{eval_output.parsed.strengths or 'No strengths mentioned.'}")

                # Areas of Concern
                st.markdown("### Areas of Concern")
                st.markdown(f"{eval_output.parsed.areas_for_concern or 'No concerns found.'}")


            # interview_questions = generate_interview_questions(job_description_input,resume_text)
            st.markdown("")
            if suggest_ques:
                # --- Interview Questions ---
                st.markdown("#### 💬 Suggested Interview Questions & Answers")
                for idx in range(0, len(interview_questions_answers.parsed.questions_answers), 2):
                    question = interview_questions_answers.parsed.questions_answers[idx]
                    answer = interview_questions_answers.parsed.questions_answers[idx + 1]
                    st.markdown(f"**{idx//2 + 1}. {question}**")
                    st.markdown(f"{answer}")
    else:
        st.warning("Please provide both a Job Description or upload a Candidate's Resume to proceed with the evaluation.")
