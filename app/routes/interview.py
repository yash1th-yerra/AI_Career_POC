from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def interview_job(job_id: str):
    return {"message": "Interview job applied successfully"}