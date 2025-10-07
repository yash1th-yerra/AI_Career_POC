# app/agents/resume_agent.py
import spacy
import PyPDF2
import docx2txt
from app.services.llm_service import get_gemini_llm
from app.services.embedding_service import embed_text, add_embedding_to_index
from app.services.db_service import insert_resume

# Load spaCy NER model for resumes (custom if available)
nlp = spacy.load("en_core_web_sm")

gemini_llm = get_gemini_llm()

class ResumeAgent:
    def __init__(self, llm_callable):
        self.llm = llm_callable

    def extract_text(self, file_path: str, file_type: str):
        if file_type.lower() == "pdf":
            text = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text()
            return text
        elif file_type.lower() == "docx":
            return docx2txt.process(file_path)
        else:
            raise ValueError("Unsupported file type")

    def parse_resume(self, text: str):
        doc = nlp(text)
        entities = {"Skills": [], "Experience": [], "Education": []}
        for ent in doc.ents:
            if ent.label_ in ["ORG", "WORK_OF_ART"]:  # Customize labels if needed
                entities["Experience"].append(ent.text)
            if ent.label_ == "EDUCATION":
                entities["Education"].append(ent.text)
            if ent.label_ == "SKILL":
                entities["Skills"].append(ent.text)
        return entities

    def score_resume(self, text: str):
        prompt = f"Score this resume for ATS compliance and keyword density:\n{text}"
        score_feedback = self.llm(prompt)
        return score_feedback

    def process_resume(self, file_path: str, file_type: str):
        text = self.extract_text(file_path, file_type)
        parsed = self.parse_resume(text)
        ats_feedback = self.score_resume(text)
        embedding = embed_text(text)
        add_embedding_to_index(embedding, id=0)  # ID can be auto-generated or DB ID
        resume_json = {
            "parsed": parsed,
            "ats_feedback": ats_feedback,
            "text": text
        }
        resume_id = insert_resume(resume_json)
        return {"resume_id": resume_id, "parsed": parsed, "ats_feedback": ats_feedback}
    
resume_agent = ResumeAgent(gemini_llm)
