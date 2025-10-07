from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def apply_job(job_id: str):
    return {"message": "Job applied successfully"}