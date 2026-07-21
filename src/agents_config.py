import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Initialize Gemini API
gemini_key = os.environ.get("GEMINI_API_KEY")
if not gemini_key:
    print("\n[System Alert]: Could not find GEMINI_API_KEY in your environment variables.\n")
else:
    genai.configure(api_key=gemini_key)

# Create a simple Study Assistant Agent using Gemini
class StudyAssistantAgent:
    def __init__(self):
        self.name = "study_assistant_agent"
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.system_instruction = """You are JobReady's AI Study Assistant — a friendly, expert career tutor embedded inside the JobReady learning platform.
You help learners who are actively following a structured weekly curriculum to become job-ready in their chosen tech career.

Your role:
- Answer questions about the current week's learning objectives, concepts, and resources.
- Explain technical concepts in simple, practical terms appropriate to the learner's level.
- Suggest how to stay on track when learners feel stuck or overwhelmed.
- Provide encouragement and study tips to keep learners motivated.
- Help clarify confusing topics from curated course materials (videos, docs, courses).

Guidelines:
1. Always be concise — keep responses under 200 words unless the question genuinely requires more depth.
2. Use bullet points or numbered steps for clarity when explaining multi-step concepts.
3. Never hallucinate URLs. If you reference a resource, only mention it by name.
4. Maintain a warm, encouraging, and professional tone — like a senior engineer mentoring a junior.
5. If context about the current role or week is provided, tailor your answer specifically to that context.
6. Never output raw JSON or code blocks unless the learner explicitly asks for code examples.
7. Do not go off-topic — stay focused on the learner's current curriculum and career goals.

You are part of the JobReady platform. The platform's mission is to help people become genuinely job-ready through structured, curated, real-world-aligned learning paths."""

    def ask(self, query, context=""):
        """Ask the Study Assistant a question"""
        try:
            full_prompt = f"{context}\n\nLearner Question: {query}" if context else query
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                )
            )
            
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

# Initialize the Study Assistant Agent
study_assistant_agent = StudyAssistantAgent()
