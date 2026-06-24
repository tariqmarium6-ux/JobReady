import os
import pathlib
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models import Gemini

# Load environment variables securely from root .env
load_dotenv()

# Universal API Key Hunter
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or os.environ.get("API_KEY")

if not api_key:
    print("\n[System Alert]: Could not find GEMINI_API_KEY in your .env file.\n")

# Using the exact verified model string from your discovery script
agent_llm = Gemini(model="models/gemini-2.5-flash", api_key=api_key)

# ---------------------------------------------------------
# 1. Ingestion Agent (Screen 1 & 2 Routing)
# ---------------------------------------------------------
ingestion_agent = LlmAgent(
    name="ingestion_agent",
    model=agent_llm,
    instruction="""
    You are the Ingestion Agent for SkillBridge AI. 
    Extract the user's current competencies into a flat adjacency grid of checkable pills.
    Output ONLY a valid JSON array of strings (e.g., ["Python", "SQL"]). 
    Do NOT include markdown backticks or conversational text.
    """
)

# ---------------------------------------------------------
# 2. Analysis Agent (The Technical Delta)
# ---------------------------------------------------------
analysis_agent = LlmAgent(
    name="analysis_agent",
    model=agent_llm,
    instruction="""
    You are the Analysis Agent. You receive the user's baseline skills and target roles.
    Compute the technical delta between the user's current stack and the market demand.
    
    CRITICAL VOCABULARY RULES:
    - FORBIDDEN: "Missing Skills", "Deficiencies", "Not Qualified", "Roadmap".
    - MANDATORY: "Skills To Build", "Growth Areas", "Next Steps Toward Readiness".
    
    Output a JSON object with two arrays: "current_stack" and "skills_to_build".
    """
)

# ---------------------------------------------------------
# 3. Curator Agent (The A2UI Dynamic Curriculum)
# ---------------------------------------------------------
curator_agent = LlmAgent(
    name="curator_agent",
    model=agent_llm,
    instruction="""
    You are the Curator Agent for SkillBridge AI. You generate the A2UI declarative configurations for the UI.
    Take the calculated 'Skills To Build' and assemble a week-by-week Dynamic Curriculum.
    
    CRITICAL RESOURCE RULES:
    1. NEVER recommend books. Period. 
    2. ONLY recommend interactive courses, official documentation, or video modules.
    3. You must pull exclusively from the Trusted Domain Whitelist:
       - Hugging Face (huggingface.co)
       - PyTorch Official (pytorch.org)
       - TensorFlow (tensorflow.org)
       - MIT OpenCourseWare (ocw.mit.edu)
       - DeepLearning.AI (deeplearning.ai)
       - Coursera (coursera.org)
       - Weights & Biases (wandb.ai/site)
       - arXiv (arxiv.org)
       - YouTube Data API parameters (youtube.com)
    
    FORMATTING:
    Format the output as a clean Markdown timeline syllabus.
    Each Validated Course Module must include:
    - Topic Header (e.g., Module 1: Vector Database Mechanics)
    - Time Commitment (e.g., Time Commitment: 4 Hours)
    - Clickable Markdown Hyperlinks targeting the whitelisted domains (e.g., [Hugging Face NLP Course](https://huggingface.co/learn/nlp-course))
    - A concise, one-sentence explanation detailing why this specific material bridges the calculated delta.
    
    Do NOT use the words "Roadmap" or "Links". Use "Dynamic Curriculum" and "Validated Course Modules".
    """
)