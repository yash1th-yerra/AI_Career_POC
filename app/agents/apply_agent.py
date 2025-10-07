# app/agents/apply_agent.py
class ApplyAgent:
    def apply(self, parsed_resume, job):
        return {"status": "applied"}

apply_agent = ApplyAgent()
