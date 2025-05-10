
from pydantic import BaseModel,Field
from typing import List

class EvaluationResult(BaseModel):
    score: int    = Field(description="Evaluation score of candidate, ranging from 1 to 100.")
    feedback: str = Field(description="Evaluation feedback.")


class InterviewQuestions(BaseModel):
    questions: List[str] = Field(description="Interview questions for candidate.")

