from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def job_job(job_id: str):
    return {"message": "Job applied successfully"}