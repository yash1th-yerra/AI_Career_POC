from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def matching_job(job_id: str):
    return {"message": "Matching job applied successfully"}