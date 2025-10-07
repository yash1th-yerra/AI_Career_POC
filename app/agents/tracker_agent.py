# app/agents/tracker_agent.py
class TrackerAgent:
    def track(self, job):
        return {"status": "tracking"}

tracker_agent = TrackerAgent()
