# app/agents/resume_agent.py
import spacy
import pdfplumber
import docx2txt
import json
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.schema import StrOutputParser
from app.services.llm_service import get_gemini_llm
from app.services.embedding_service import embed_text, add_embedding_to_index
from app.services.db_service import insert_resume

# Load spaCy NER model for resumes (custom if available)
nlp = spacy.load("en_core_web_sm")

gemini_llm = get_gemini_llm()

class ResumeAgent:
    def __init__(self, llm_callable):
        self.llm = llm_callable
        self._setup_resume_parser_chain()

    def _setup_resume_parser_chain(self):
        """Setup the comprehensive resume parsing chain with role recommendations and experience level."""
        prompt = ChatPromptTemplate.from_template("""
You are an expert Resume Intelligence Agent that extracts structured data and evaluates resumes for ATS compatibility.

Analyze the following resume text and return ONLY a valid JSON object with these exact keys:

{{
  "name": "",
  "location": "",
  "summary": "",
  "skills": [],
  "extra_skills": [],
  "work_experience": [],
  "projects": [],
  "certifications": [],
  "education": [],
  "experience_level": "",
  "recommended_roles": [],
  "ats_feedback": {{
    "score": 0,
    "summary": "",
    "strengths": [],
    "improvements": []
  }}
}}

CRITICAL EXTRACTION RULES FOR ALL SECTIONS:

1. **NAME**: Extract the full name exactly as written, using the most prominent name (usually at the top).

2. **LOCATION**: Extract specific city and country from contact info, address, or personal details. Format as "City, Country" (e.g., "Chennai, India", "Bangalore, India"). If no city is specified, use " Country".

3. **SUMMARY**: Look for sections titled "Summary", "Objective", "Profile", "About Me", "Career Summary". Extract complete professional summary.

4. **SKILLS**: Extract skills ONLY from dedicated "Skills", "Technical Skills", "Core Skills", "Programming Languages", or similar sections:
   - ONLY include skills explicitly listed in a dedicated skills section
   - Programming languages, frameworks, tools, technologies mentioned in skills section
   - Return as array of individual skills from the skills section only

5. **EXTRA_SKILLS**: Extract additional skills mentioned in other contexts:
   - Skills mentioned in work experience descriptions
   - Technologies used in projects
   - Skills mentioned in certifications or education
   - Any other skills not in the main skills section
   - Return as array of individual skills from non-skills sections

6. **WORK_EXPERIENCE**: Extract each position with:
   - Job title, company, duration, location
   - Key responsibilities and achievements
   - Format as structured objects with consistent fields

7. **PROJECTS**: Extract personal/academic projects with:
   - Project name, duration, technologies used
   - Brief description and key features
   - Any notable achievements or results

8. **CERTIFICATIONS**: Extract all certifications with:
   - Certification name, issuing organization, year
   - Include online courses, professional certifications

9. **EDUCATION**: Extract educational background with:
   - Degree, institution, graduation year
   - Relevant coursework or achievements

10. **EXPERIENCE_LEVEL**: Analyze the candidate's work experience and determine their experience level:
    - "Entry Level" (0-1 years): Fresh graduates, internships, or minimal professional experience
    - "Junior" (1-3 years): Some professional experience, early career roles
    - "Mid-Level" (3-7 years): Solid professional experience, can work independently
    - "Senior" (7-12 years): Advanced experience, can lead projects and mentor others
    - "Lead/Principal" (12+ years): Expert level, can architect solutions and lead teams
    - Consider total years of experience, complexity of roles, leadership responsibilities
    - Return a single string value

11. **RECOMMENDED_ROLES**: Based on the candidate's skills, experience, education, and projects, recommend 2-3 specific job roles they would be suitable for:
    - Consider their technical skills, domain expertise, and career progression
    - Include roles that match their current skill level and potential growth areas
    - Format as array of role titles (e.g., ["Software Engineer", "Data Analyst", "Frontend Developer"])
    - Be specific and industry-relevant

12. **ATS_FEEDBACK**: Provide objective evaluation:
    - score: 0-100 based on ATS compatibility
    - summary: Brief assessment
    - strengths: Positive aspects
    - improvements: Areas for enhancement 

Guidelines:
- Detect section names dynamically (e.g., "Profile", "About Me", "Objective" → summary).
- CRITICAL: Skills extraction must be source-aware:
  * "skills" array: ONLY from dedicated skills sections (Skills, Technical Skills, Core Skills, Programming Languages, etc.)
  * "extra_skills" array: Skills mentioned in work experience, projects, certifications, education, or other contexts
- Extract job/project details separately.
- For EXPERIENCE_LEVEL: Analyze total years of professional experience, role complexity, and leadership indicators
- For RECOMMENDED_ROLES: Analyze the candidate's profile holistically and suggest roles that align with their skills and experience level
- Be consistent and produce clean JSON only.
- Prioritize accuracy over completeness.
- IMPORTANT: Return ONLY the JSON object, no additional text or explanations.

Resume Text:
{resume_text}
""")
        
        self.resume_parser_chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_parser=StrOutputParser()
        )

    def extract_text(self, file_path: str, file_type: str):
        """Extract text from PDF or DOCX resume."""
        if file_type.lower() == "pdf":
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                max_pages = min(2, len(pdf.pages))  # Limit to first 2 pages for efficiency
                for i in range(max_pages):
                    text_parts.append(pdf.pages[i].extract_text() or "")
            text = "\n".join(text_parts)
        elif file_type.lower() == "docx":
            text = docx2txt.process(file_path)
        else:
            raise ValueError("Unsupported file type")

        # Optional cleaning
        text = text.replace('\n', ' ').replace('\t', ' ').strip()
        return text

    def parse_resume_comprehensive(self, text: str):
        """Parse resume using comprehensive LLM analysis with role recommendations and experience level."""
        try:
            raw_output = self.resume_parser_chain.run({"resume_text": text})
            structured_output = json.loads(raw_output)
            return structured_output
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM output as JSON: {e}")
        except Exception as e:
            raise ValueError(f"Error during resume parsing: {e}")

    def process_resume(self, file_path: str, file_type: str):
        """Process resume with comprehensive analysis including role recommendations and experience level."""
        text = self.extract_text(file_path, file_type)
        parsed_data = self.parse_resume_comprehensive(text)
        
        # Create embedding for the resume text
        embedding = embed_text(text)
        add_embedding_to_index(embedding, id=0)  # ID can be auto-generated or DB ID
        
        # Store in database
        resume_json = {
            "parsed": parsed_data,
            "text": text
        }
        resume_id = insert_resume(resume_json)
        
        return {
            "resume_id": resume_id, 
            "parsed": parsed_data,
            "experience_level": parsed_data.get("experience_level", ""),
            "recommended_roles": parsed_data.get("recommended_roles", []),
            "ats_feedback": parsed_data.get("ats_feedback", {})
        }
    
resume_agent = ResumeAgent(gemini_llm)
