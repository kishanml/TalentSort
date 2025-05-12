
from pydantic import BaseModel,Field
from typing import List, Dict

class EvaluationResult(BaseModel):
    Introduction: str = Field(description="Candidate's Introduction & Summary")

    Education_score: int = Field(description="Candidate's score in Education")
    Education_feedback: str = Field(description="Feedback for Education")

    Experience_score: int = Field(description="Candidate's score in Experience")
    Experience_feedback: str = Field(description="Feedback for Experience")

    Required_Skills_score: int = Field(description="Candidate's score in Required Skills")
    Required_Skills_feedback: str = Field(description="Feedback for Required Skills")

    Responsibilities_score: int = Field(description="Candidate's score in Responsibilities")
    Responsibilities_feedback: str = Field(description="Feedback for Responsibilities")

    Strengths: str = Field(description="Candidate's Strengths")

    Concerns: str = Field(description="Candidate's areas of concern")


class InterviewQuestions(BaseModel):
    questions_answers: List[str] = Field(description="Interview questions and answers for candidate.")

