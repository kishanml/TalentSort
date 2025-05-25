
import os
from google import genai
from .prompts import interview_question_prompt,score_evaluation_prompt_2
from .models import EvaluationResult,InterviewQuestions

# from dotenv import load_dotenv
# load_dotenv()

#TODO : Will add this to streamlit secrets later. Dont copy it pls. 
# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_API_KEY="AIzaSyDcU_qZ1VbWOoRogappbV0NtDTn_xzhlOw"



def evaluate_candidate(job_description, resume_str,additional_instruction="Evaluate this candidate !", system_prompt=score_evaluation_prompt_2) -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)

    
    prompt_parts = [
        system_prompt,
        "Job Description:",
        job_description,
        "\n--- Candidate Resume ---\n",
        resume_str,
        "\n--- ADDITIONAL INSTRUCTIONS (CRITICAL) ---\n",
        additional_instruction,
         "\n--- END OF INSTRUCTIONS ---\n"
    ]
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt_parts,
        config={
            'response_mime_type': 'application/json',
            'response_schema': EvaluationResult,
            'temperature': 0.1,
            "top_p":0.9,
            "top_k":40
        },
    )
    return response



def generate_interview_questions(job_description, resume_str,system_prompt=interview_question_prompt,additional_instruction="Generate well suited questions.") -> str:
    client = genai.Client(api_key=GEMINI_API_KEY)

    

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
           system_prompt,
            "Job Description:",
            job_description,
            "Candidate Resume:",
            resume_str,
            "Additional Instructions:",
            additional_instruction
        ],
        
        config={
            'response_mime_type': 'application/json',
            'response_schema': InterviewQuestions,
            'temperature': 0.2,
        },
    )
    return response