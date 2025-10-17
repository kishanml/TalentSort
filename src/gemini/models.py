
from pydantic import BaseModel,Field
from typing import List, Dict

class EvaluationResult(BaseModel):
    evaluation_summary: str = Field(description="Candidate's Introduction & Summary")

    extracted_education: list[str] = Field(description="Candidate's Education Details")
    extracted_experience: list[str] = Field(description="Candidate's Professional Experience Details")

    required_skills_score: int = Field(description="Candidate's score in Required Skills")
    required_skills_feedback: str = Field(description="Feedback for Required Skills")

    responsibilities_score: int = Field(description="Candidate's score in Responsibilities")
    responsibilities_feedback: str = Field(description="Feedback for Responsibilities")

    overall_relevance_score: int = Field(description="Candidate's score in overallProfileRelevance")
    overall_relevance_feedback: str = Field(description="Feedback for overallProfileRelevance")

    strengths: str = Field(description="Candidate's Strengths")
    areas_for_concern: str = Field(description="Candidate's areas of concern")




class InterviewQuestions(BaseModel):
    questions_answers: List[str] = Field(description="Interview questions and answers for candidate.")

