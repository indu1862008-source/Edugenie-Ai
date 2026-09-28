from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import settings
from schemas import (
    QARequest,
    ExplainRequest,
    QuizRequest,
    SummaryRequest,
    LearningPathRequest,
    TextResponse,
    QuizResponse,
    LearningPathResponse,
)

from qna import answer_question
from explanation_module import explain_concept
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations
from gemini_client import GeminiServiceError


app = FastAPI(
    title="EduGenie",
    description="Google Gemini Powered Learning Assistant",
    version="1.0.0",
)


@app.exception_handler(GeminiServiceError)
async def gemini_service_error(
    request: Request,
    exc: GeminiServiceError,
):
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc)},
    )


# ---------------------------------------------------------
# Static files and templates
# ---------------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

templates = Jinja2Templates(
    directory="templates"
)


# ---------------------------------------------------------
# Home page
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "app_name": settings.app_name,
        },
    )


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "gemini_configured": bool(settings.gemini_api_key),
        "gemini_model": settings.gemini_model,
        "explanation_provider": settings.explanation_provider,
    }


# ---------------------------------------------------------
# Question Answering
# ---------------------------------------------------------

@app.post("/qa", response_model=TextResponse)
async def qa(payload: QARequest):

    result = await answer_question(
        payload.question
    )

    return TextResponse(
        result=result
    )


# ---------------------------------------------------------
# Concept Explanation
# ---------------------------------------------------------

@app.post("/explain", response_model=TextResponse)
async def explain(payload: ExplainRequest):

    result = await explain_concept(
        payload.topic
    )

    return TextResponse(
        result=result
    )


# ---------------------------------------------------------
# Quiz Generation
# ---------------------------------------------------------

@app.post("/quiz", response_model=QuizResponse)
async def quiz(payload: QuizRequest):

    return await generate_quiz(
        payload.text
    )


# ---------------------------------------------------------
# Summarization
# ---------------------------------------------------------

@app.post("/summarize", response_model=TextResponse)
async def summarize(payload: SummaryRequest):

    result = await summarize_text(
        payload.text
    )

    return TextResponse(
        result=result
    )


# ---------------------------------------------------------
# Learning Path
# ---------------------------------------------------------

@app.post(
    "/learn/recommendations",
    response_model=LearningPathResponse,
)
async def learning_recommendations(
    payload: LearningPathRequest,
):

    return await get_learning_recommendations(
        payload.topic,
        payload.level,
    )


# ---------------------------------------------------------
# Local execution
# ---------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )