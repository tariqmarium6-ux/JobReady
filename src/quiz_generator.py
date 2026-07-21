import os
import json
import asyncio
import hashlib
import time
import httpx
from dotenv import load_dotenv

# Load environment variables (works locally)
load_dotenv()

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

groq_api_key = _get_secret("GROQ_API_KEY")
gemini_api_key = _get_secret("GEMINI_API_KEY")

# We only use valid Gemini API keys starting with AIzaSy for REST
GEMINI_KEYS = [k.strip() for k in [gemini_api_key] if k and k.startswith("AIzaSy")]
if not GEMINI_KEYS:
    # Try to read multiple keys from GEMINI_API_KEYS env variable
    multi_keys_raw = _get_secret("GEMINI_API_KEYS")
    if multi_keys_raw:
        GEMINI_KEYS = [k.strip() for k in multi_keys_raw.split(",") if k.strip().startswith("AIzaSy")]
if not GEMINI_KEYS:
    # Final hardcoded fallback keys
    GEMINI_KEYS = ["AIzaSyBbsPI0VypOYJtWpHGZIJlhBTyI3sGiCI8", "AIzaSyAZu_fVAbzSGenWipeZmkXnThxS9jD9jPM"]

GEMINI_KEY_COOLDOWN = {key: 0.0 for key in GEMINI_KEYS}
current_engine = "groq-70b"

def get_available_gemini_key():
    now = time.time()
    for key in GEMINI_KEYS:
        if GEMINI_KEY_COOLDOWN.get(key, 0) <= now:
            return key, 0
    soonest_key = min(GEMINI_KEYS, key=lambda k: GEMINI_KEY_COOLDOWN.get(k, 0))
    wait = max(0, GEMINI_KEY_COOLDOWN[soonest_key] - now)
    return None, wait

async def query_direct_gemini_async(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.2
        }
    }
    async with httpx.AsyncClient(timeout=45.0) as client:
        res = await client.post(url, json=payload)
        if res.status_code == 429:
            raise httpx.HTTPStatusError("429 Rate Limit", request=res.request, response=res)
        if res.status_code == 503:
            raise httpx.HTTPStatusError("503 Unavailable", request=res.request, response=res)
        res.raise_for_status()
        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

async def query_direct_groq(prompt, model_name, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system", 
                "content": "You are a university assessment generator. Respond strictly with a raw JSON object containing the quiz questions."
            },
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2
    }
    async with httpx.AsyncClient(timeout=45.0) as client:
        res = await client.post(url, json=payload, headers=headers)
        if res.status_code == 429:
            raise httpx.HTTPStatusError("429 Rate Limit Exceeded", request=res.request, response=res)
        res.raise_for_status()
        res_json = res.json()
        return res_json["choices"][0]["message"]["content"]

async def query_llm(prompt):
    global current_engine
    retries = 8
    while retries > 0:
        try:
            if current_engine == "groq-70b" and groq_api_key:
                try:
                    return await query_direct_groq(prompt, "llama-3.3-70b-versatile", groq_api_key)
                except Exception as e:
                    if "429" in str(e):
                        current_engine = "groq-8b"
                        await asyncio.sleep(4)
                        continue
                    raise e
            elif current_engine == "groq-8b" and groq_api_key:
                try:
                    return await query_direct_groq(prompt, "llama-3.1-8b-instant", groq_api_key)
                except Exception as e:
                    if "429" in str(e):
                        current_engine = "gemini"
                        await asyncio.sleep(6)
                        continue
                    raise e
            else:  # gemini
                key, wait_secs = get_available_gemini_key()
                if key is None:
                    await asyncio.sleep(min(wait_secs + 2, 30))
                    current_engine = "groq-70b"
                    continue
                try:
                    return await query_direct_gemini_async(prompt, key)
                except httpx.HTTPStatusError as e:
                    if "429" in str(e):
                        GEMINI_KEY_COOLDOWN[key] = time.time() + 70
                        continue
                    raise e
        except Exception as ex:
            retries -= 1
            await asyncio.sleep(4)
            current_engine = "groq-70b"
            
    raise RuntimeError("Query failed after all retries.")

def get_weekly_quiz_sync(role_name: str, week_num: int, week_goal: str, objectives: list, db_provider) -> dict:
    """Synchronous version of generate_weekly_quiz for safe, bulletproof execution inside Streamlit popovers."""
    prompt = f"""
    Generate exactly 5 multiple-choice questions for the following syllabus week:
    Career Roadmap: {role_name}
    Week: {week_num}
    Goal: {week_goal}
    Learning Objectives: {json.dumps(objectives, indent=2)}

    Requirements:
    1. Generate exactly 5 questions.
    2. Assess ONLY what is covered in this specific week's goal and objectives.
    3. Each question must have exactly 4 choices (options).
    4. Provide the 0-indexed correct_answer_index.
    5. Provide a detailed, pedagogical explanation.

    Your response must match the following JSON schema:
    {{
      "questions": [
        {{
          "question": "Question text here?",
          "options": ["Option A", "Option B", "Option C", "Option D"],
          "correct_answer_index": 0,
          "explanation": "pedagogical explanation."
        }}
      ]
    }}
    """
    
    prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
    
    # 1. Check Cache
    try:
        cached = db_provider.get_cached_quiz(role_name, week_num, prompt_hash)
        if cached:
            return cached
    except Exception as _ce:
        pass

    # 2. Try synchronous LLM call (Groq)
    g_key = _get_secret("GROQ_API_KEY")
    if g_key:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {g_key}", "Content-Type": "application/json"}
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are a university assessment generator. Respond strictly with a raw JSON object containing the quiz questions."},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    res_json = res.json()
                    cleaned = res_json["choices"][0]["message"]["content"].strip()
                    start = cleaned.find("{")
                    end = cleaned.rfind("}") + 1
                    if start != -1 and end != -1:
                        cleaned = cleaned[start:end]
                    quiz_data = json.loads(cleaned)
                    if "questions" in quiz_data and len(quiz_data["questions"]) == 5:
                        db_provider.save_cached_quiz(role_name, week_num, prompt_hash, quiz_data)
                        return quiz_data
        except Exception as _ge:
            print(f"[Quiz LLM Sync Warning]: {_ge}")

    # 3. Fallback Quiz tailored to week
    fallback_quiz = {
        "questions": [
            {
                "question": f"Which of the following is the primary goal of {role_name} in Week {week_num}?",
                "options": [f"Master the core objective: {week_goal}", "Setup legacy database clusters", "Refactor server deployment scripts", "Modify global UI CSS parameters"],
                "correct_answer_index": 0,
                "explanation": f"The primary focus for this week is: {week_goal}."
            },
            {
                "question": f"Which skill or methodology is emphasized in Week {week_num}'s learning plan?",
                "options": [objectives[0] if objectives else "Core concept mastery", "Unrelated framework configuration", "Deprecated API integration", "Manual log parsing"],
                "correct_answer_index": 0,
                "explanation": "Mastering the weekly learning objectives ensures maximum career readiness."
            },
            {
                "question": "What is the key benefit of completing this week's practice task?",
                "options": ["Building practical hands-on portfolio experience", "Skipping prerequisite checks", "Earning badges without testing", "Disabling automatic link validation"],
                "correct_answer_index": 0,
                "explanation": "Hands-on projects reinforce theoretical knowledge and build a verifiable portfolio."
            },
            {
                "question": "How does completing weekly progress milestones help your job readiness?",
                "options": ["It validates core competencies and earns progress badges", "It resets the study pace slider", "It deletes cached quiz records", "It hides upcoming curriculum weeks"],
                "correct_answer_index": 0,
                "explanation": "Tracking milestones ensures consistent learning progress toward your career goal."
            },
            {
                "question": "What is the recommended approach when reviewing curated learning resources?",
                "options": ["Follow resources sequentially and complete the practical exercises", "Skip all documentation links", "Only read the first 5 minutes of each video", "Rely exclusively on memorization"],
                "correct_answer_index": 0,
                "explanation": "Sequential study combined with active practice yields the highest skill retention."
            }
        ]
    }
    
    try:
        db_provider.save_cached_quiz(role_name, week_num, prompt_hash, fallback_quiz)
    except Exception:
        pass
        
    return fallback_quiz

async def generate_weekly_quiz(role_name: str, week_num: int, week_goal: str, objectives: list, db_provider) -> dict:
    """Async wrapper for backward compatibility."""
    return get_weekly_quiz_sync(role_name, week_num, week_goal, objectives, db_provider)


