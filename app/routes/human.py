from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def human_job(job_id: str):
    return {"message": "Human job applied successfully"}