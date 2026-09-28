from typing import List

from pydantic import BaseModel, Field


class QARequest(BaseModel):
    question: str = Field(min_length=1, max_length=20000)


class ExplainRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=20000)


class QuizRequest(BaseModel):
    text: str = Field(min_length=1, max_length=12000)


class SummaryRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20000)


class LearningPathRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=20000)
    level: str = Field(min_length=1, max_length=100)


class TextResponse(BaseModel):
    result: str


class QuizQuestion(BaseModel):
    question: str
    options: List[str] = Field(min_length=4, max_length=4)
    correct_answer: str
    explanation: str


class QuizResponse(BaseModel):
    questions: List[QuizQuestion] = Field(min_length=3, max_length=3)


class LearningStep(BaseModel):
    stage: str
    topics: List[str] = Field(min_length=1)
    estimated_time: str
    resources: List[str] = Field(min_length=1)


class LearningPathResponse(BaseModel):
    topic: str
    level: str
    steps: List[LearningStep] = Field(min_length=3, max_length=8)
    study_tips: List[str] = Field(min_length=3, max_length=8)
