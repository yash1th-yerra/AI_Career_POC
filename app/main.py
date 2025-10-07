from fastapi import FastAPI
from app.routes import resume, job, matching, apply, tracker, interview, human


app = FastAPI(title="AI Career System")
# Register routes
app.include_router(resume.router, prefix="/resume")
app.include_router(job.router, prefix="/job")
app.include_router(matching.router, prefix="/matching")
app.include_router(apply.router, prefix="/apply")
app.include_router(tracker.router, prefix="/tracker")
app.include_router(interview.router, prefix="/interview")
app.include_router(human.router, prefix="/human")
@app.get("/")
def home():
    return {"message": "Welcome to AI Career System 🚀"}