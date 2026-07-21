import os
import json
import asyncio
from google.genai import Client

def _get_secret(key: str) -> str:
    """Read from env first (local .env), then fall back to st.secrets (Streamlit Cloud)."""
    val = os.environ.get(key, "")
    if not val:
        try:
            import streamlit as st
            val = st.secrets.get(key, "")
        except Exception:
            pass
    return val or ""

def get_gemini_client():
    # 1. Try primary GEMINI_API_KEY from environment / st.secrets first
    env_key = _get_secret("GEMINI_API_KEY")
    if env_key:
        return Client(api_key=env_key)
    
    # 2. Extract fallback keys safely from the environment string if primary fails
    fallback_raw = _get_secret("GEMINI_FALLBACK_KEYS")
    gemini_keys = [key.strip() for key in fallback_raw.split(",") if key.strip()]
    
    # Try other keys in rotation
    for key in gemini_keys:
        try:
            return Client(api_key=key)
        except Exception:
            continue
    return None

def generate_emergency_resource(topic, goal, objectives, difficulty, duration):
    """
    Calls Gemini to generate an emergency fallback resource that fits
    the week's topic and learning objectives exactly, using stable official sources.
    """
    client = get_gemini_client()
    if not client:
        return get_default_emergency_fallback(topic, difficulty, duration)
        
    prompt = f"""
    You are an expert university curriculum editor. An educational resource has become unavailable.
    Generate a high-quality, verified emergency replacement learning resource for the following:
    
    Topic: {topic}
    Weekly Goal: {goal}
    Learning Objectives: {", ".join(objectives)}
    Difficulty Level: {difficulty}
    Estimated Duration: {duration}
    
    Requirements:
    1. The replacement MUST cover the exact same topic and objectives.
    2. Recommend a highly stable, active URL from a top-tier provider (e.g. MIT OpenCourseWare, Python Docs, MDN Web Docs, PostgreSQL Tutorial, Docker Docs, or a major freeCodeCamp/Mosh video).
    3. The URL must be general and highly stable (e.g. documentation roots or main tutorial indices) so it is guaranteed to never break.
    4. Respond strictly with a JSON object following this format:
    {{
      "title": "Name of the resource",
      "provider": "The name of the platform/author (e.g. MIT, freeCodeCamp, PostgreSQL Docs)",
      "url": "A fully valid, active URL",
      "type": "video" | "Documentation" | "Course" | "Article",
      "trust_score": a float between 9.0 and 10.0 (e.g. 9.8),
      "educational_quality": "Excellent",
      "difficulty": "{difficulty}",
      "estimated_duration": "{duration}",
      "provider_type": "University" | "Official Docs" | "Industry" | "Community"
    }}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )
        if response and response.text:
            data = json.loads(response.text.strip())
            return data
    except Exception as e:
        print(f"[AI Fallback Error]: {e}")
        
    return get_default_emergency_fallback(topic, difficulty, duration)

def get_default_emergency_fallback(topic, difficulty, duration):
    """Returns a safe, stable fallback resource if Gemini API call fails."""
    # Mapping of general skills to safe documentation homepages
    t_lower = topic.lower()
    if "python" in t_lower:
        url = "https://docs.python.org/3/tutorial/"
        title = "Python Tutorial Documentation"
        provider = "Python Software Foundation"
        ptype = "Official Docs"
    elif "sql" in t_lower or "database" in t_lower or "postgres" in t_lower:
        url = "https://www.postgresqltutorial.com/"
        title = "PostgreSQL Tutorial Core Guide"
        provider = "PostgreSQL Tutorial"
        ptype = "Official Docs"
    elif "docker" in t_lower or "container" in t_lower:
        url = "https://docs.docker.com/get-started/"
        title = "Docker Getting Started Documentation"
        provider = "Docker Docs"
        ptype = "Official Docs"
    elif "git" in t_lower:
        url = "https://git-scm.com/doc"
        title = "Git Reference Documentation"
        provider = "Git Docs"
        ptype = "Official Docs"
    elif "react" in t_lower or "frontend" in t_lower or "javascript" in t_lower:
        url = "https://react.dev/reference/react"
        title = "React Core API Reference"
        provider = "React Docs"
        ptype = "Official Docs"
    else:
        url = "https://www.freecodecamp.org/learn/"
        title = "freeCodeCamp Learning Directory"
        provider = "freeCodeCamp"
        ptype = "Community"

    return {
        "title": title,
        "provider": provider,
        "url": url,
        "type": "Documentation",
        "trust_score": 9.5,
        "educational_quality": "Excellent",
        "difficulty": difficulty,
        "estimated_duration": duration,
        "provider_type": ptype
    }