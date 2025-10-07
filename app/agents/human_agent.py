# app/agents/human_agent.py
class HumanAgent:
    def review(self, parsed_resume):
        return {"feedback": "looks good"}

human_agent = HumanAgent()
