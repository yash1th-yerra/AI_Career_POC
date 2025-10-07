from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def tracker_job(job_id: str):
    return {"message": "Tracker job applied successfully"}