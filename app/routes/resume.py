# app/routes/resume.py
from fastapi import APIRouter, UploadFile
from app.agents.resume_agent import resume_agent
import shutil

router = APIRouter()

@router.post("/analyze")
async def analyze_resume_endpoint(file: UploadFile):
    # Save file temporarily
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_type = file.filename.split(".")[-1]
    result = resume_agent.process_resume(temp_path, file_type)
    return result
