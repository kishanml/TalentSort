
import os
from google import genai
from .prompts import interview_question_prompt,score_evaluation_prompt
from .models import EvaluationResult,InterviewQuestions



class Evaluator:

    def __init__(self, api_key : str, *,\
                 model_name : str ="gemini-2.0-flash"):

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
    

    def evaluate_candidate( self, job_description : str , \
                           resume_str : str , * ,additional_instruction : str ="Evaluate this candidate !",\
                           system_prompt : str = score_evaluation_prompt) -> str:
        
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
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt_parts,
            config={
                'response_mime_type': 'application/json',
                'response_schema': EvaluationResult,
                'temperature': 0,
            },
        )
        return response



    def generate_interview_questions(self, job_description : str , resume_str : str ,\
                                    system_prompt : str = interview_question_prompt,\
                                    additional_instruction : str = "Generate well suited questions.") -> str:
        

        response = self.client.models.generate_content(
            model=self.model_name,
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