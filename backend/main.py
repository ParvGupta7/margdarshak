"""
main.py
-------
FastAPI application entry point.

Routes:
  POST /analyze      — Upload PDF, run full 9-step pipeline
  POST /jobs         — Fetch live jobs for a role + location
  POST /chat         — Send message to chatbot
  GET  /health       — Health check
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# Pipeline imports
from pipeline.extractor import extract_text_from_pdf
from pipeline.preprocessor import preprocess
from pipeline.parser import parse_entities
from pipeline.skill_extractor import extract_skills
from pipeline.job_classifier import classify_job_roles
from pipeline.gap_analyzer import analyze_gaps
from pipeline.course_recommender import recommend_courses
from pipeline.job_matcher import fetch_jobs
from chatbot.bot import chat

app = FastAPI(
    title="MargDarshak API",
    description="AI Resume Analyzer and Career Guidance Platform",
    version="1.0.0"
)

# Allow requests from the React frontend (running on localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Request/Response Models ----------

class ChatRequest(BaseModel):
    message: str
    analysis: dict
    history: list = []


class JobRequest(BaseModel):
    job_title: str
    location: Optional[str] = None


# ---------- Routes ----------

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "MargDarshak API"}


@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    """
    Full resume analysis pipeline.
    Accepts a PDF file, runs all 9 steps, returns complete analysis.
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Read file bytes
    pdf_bytes = await file.read()

    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(pdf_bytes) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")

    # ---- Step 1: Extract text ----
    extraction = extract_text_from_pdf(pdf_bytes)
    if extraction["status"] == "error":
        raise HTTPException(status_code=422, detail=extraction["message"])

    raw_text = extraction["raw_text"]

    # ---- Step 2: Preprocess ----
    preprocessing = preprocess(raw_text)

    # ---- Step 3: Parse entities ----
    entities = parse_entities(raw_text)

    # ---- Step 4: Extract skills ----
    skills = extract_skills(
        preprocessing["clean_text"],
        preprocessing["tokens"]
    )

    # ---- Step 5: Classify job roles ----
    job_roles = classify_job_roles(skills["matched_skills"])

    # ---- Step 6: Skill gap analysis ----
    gaps = analyze_gaps(
        skills["matched_skills"],
        job_roles["top_roles"]
    )

    # ---- Step 7: Course recommendations ----
    courses = recommend_courses(gaps["gaps"])

    # ---- Step 8: Job matching (auto-fetch for best role) ----
    best_role = job_roles.get("best_match", {})
    job_title = best_role.get("role", "Software Engineer") if best_role else "Software Engineer"
    location = entities.get("location")
    jobs = fetch_jobs(job_title, location)

    # ---- Assemble full response ----
    return {
        "status": "success",
        "filename": file.filename,
        "pipeline": {
            "step1_extraction": {
                "char_count": extraction["char_count"],
                "word_count": extraction["word_count"],
                "raw_text_preview": raw_text[:400]
            },
            "step2_preprocessing": {
                "stages": preprocessing["stages"],
                "token_count": preprocessing["token_count"]
            },
            "step3_entities": entities,
            "step4_skills": skills,
            "step5_job_roles": job_roles,
            "step6_gaps": gaps,
            "step7_courses": courses,
            "step8_jobs": jobs
        },
        # Flattened for easy frontend consumption
        "entities": entities,
        "skills": skills,
        "job_roles": job_roles,
        "gaps": gaps,
        "courses": courses,
        "jobs": jobs
    }


@app.post("/jobs")
def get_jobs(request: JobRequest):
    """Fetch jobs for a specific role and location (user-adjustable)."""
    result = fetch_jobs(request.job_title, request.location)
    return result


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    """Chatbot endpoint. Receives message + full analysis context."""
    result = chat(request.message, request.analysis, request.history)
    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
