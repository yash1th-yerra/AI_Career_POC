# app/agents/job_agent.py
class JobAgent:
    def fetch_jobs(self, parsed_resume):
        return [{"job_title": "Software Engineer", "company": "XYZ"}]

job_agent = JobAgent()
