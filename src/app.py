import os
import shutil
import streamlit as st
from services import get_text_from_resume
from gemini import evaluate_candidate,generate_interview_questions


SAVE_FOLDER_DIR = "resumes"
VIDEO_UPLOAD_PATH = None

if os.path.exists(SAVE_FOLDER_DIR):
    shutil.rmtree(SAVE_FOLDER_DIR)
os.makedirs(SAVE_FOLDER_DIR)

st.set_page_config(
    page_title="Talent Sort", 
    layout="wide",
)


st.markdown("""
<style>
.stApp {
    color : white;
}
.stTextInput > label, .stFileUploader label, .stTextArea label {
    font-weight: bold;
}
.stButton>button {
    color: white;
    font-weight: bold;
    padding: 10px 20px;
    border: 1px solid ;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    justify-content: center;
    width: 50%;
}


/* Style for the main title */
h1 {
    color: #1E88E5; /* Blue color for title */
    text-align: center;
    margin-bottom: 20px;
}
/* Style for subheaders/section titles */
h2 {
    margin-top: 20px;
    margin-bottom: 10px;
    border-bottom: 2px solid #1E88E5; /* Underline subheaders */
    padding-bottom: 5px;
}
/* Style for input areas */
.stTextArea, .stFileUploader, .stTextInput {
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #cccccc;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.1); /* Subtle shadow */
    margin-bottom: 15px; /* Add space below inputs */
}

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
            VIDEO_UPLOAD_PATH = os.path.join(SAVE_FOLDER_DIR,resume_input.name)
            with open(VIDEO_UPLOAD_PATH, mode='wb') as f:
                f.write(resume_input.read())  


    with col3:
        extra_prompt = st.text_area(
            label='🧠 Additional Instructions (Optional)', 
            height=350, 
            value="Evaluate this candidate !",
            help="e.g., 'Prioritize cloud computing experience', 'Look for leadership examples'."
        )

    # --- Submit Button ---
    st.markdown("---") 
    col = st.columns(7)[3] 
    with col:
        submit_button = st.form_submit_button(label='Evaluate')


if submit_button:
    if job_description_input and resume_input:
        with st.spinner("Evaluating candidate talent..."):
            resume_text = get_text_from_resume(VIDEO_UPLOAD_PATH)
            eval_output = evaluate_candidate(job_description=job_description_input,\
                               resume_str=resume_text,
                               additional_instruction=extra_prompt)
            
             # Generate interview questions
            interview_questions = generate_interview_questions(
                job_description_input, resume_text
            )
            
            st.markdown("---")
            st.subheader("🎯 Evaluation Results")

            score = eval_output.parsed.score
            score_color_bg = "#333"
            score_text_color = "white"
            if score >= 65:
                score_color_bg = "#4CAF50" 
            elif score >= 50:
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
                feedback_text = eval_output.parsed.feedback

                st.markdown(feedback_text)

            # interview_questions = generate_interview_questions(job_description_input,resume_text)
            st.markdown("")

            # --- Interview Questions ---
            st.markdown("#### 💬 Suggested Interview Questions")
            for idx, question in enumerate(interview_questions.parsed.questions, start=1):
                st.markdown(f"**{idx}.** {question}")
    else:
        st.warning("Please provide both a Job Description or upload a Candidate's Resume to proceed with the evaluation.")
