import os
import json
import asyncio
import hashlib
import time
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY", "")
gemini_api_key = os.getenv("GEMINI_API_KEY", "")

# We only use valid Gemini API keys starting with AIzaSy for REST
GEMINI_KEYS = [k.strip() for k in [gemini_api_key] if k and k.startswith("AIzaSy")]
if not GEMINI_KEYS:
    # Check if there are other keys configured or fallback
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

async def generate_weekly_quiz(role_name: str, week_num: int, week_goal: str, objectives: list, db_provider) -> dict:
    """Check cache, or generate exactly 5 multiple choice questions for the week's objectives."""
    
    # 1. Build prompt
    prompt = f"""
    Generate exactly 5 multiple-choice questions for the following syllabus week:
    Career Roadmap: {role_name}
    Week: {week_num}
    Goal: {week_goal}
    Learning Objectives: {json.dumps(objectives, indent=2)}

    Requirements:
    1. Generate exactly 5 questions.
    2. Assess ONLY what is covered in this specific week's goal and objectives. Do NOT ask outside this week's scope.
    3. Each question must have exactly 4 choices (options).
    4. Provide the 0-indexed correct_answer_index (0 for options[0], 1 for options[1], etc.).
    5. Provide a detailed, pedagogical explanation explaining why the correct choice is right.

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
    
    # 2. Compute prompt hash for versioned caching
    prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
    
    # 3. Check Cache
    cached = db_provider.get_cached_quiz(role_name, week_num, prompt_hash)
    if cached:
        return cached

    # 4. Generate via LLM
    try:
        res_text = await query_llm(prompt)
        cleaned = res_text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
            
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end != -1:
            cleaned = cleaned[start:end]
            
        quiz_data = json.loads(cleaned)
        
        # Verify schema
        if "questions" in quiz_data and len(quiz_data["questions"]) == 5:
            # Save to cache
            db_provider.save_cached_quiz(role_name, week_num, prompt_hash, quiz_data)
            return quiz_data
    except Exception as e:
        print(f"[ERROR]: Failed to generate LLM quiz for {role_name} Week {week_num}: {e}")
        
    # Static fallback in case of rate limits or failures (so app never breaks)
    fallback_quiz = {
        "questions": [
            {
                "question": f"Which of the following is a primary objective of {role_name} during Week {week_num}?",
                "options": [f"Master the core week goal: {week_goal}", "Build a random cloud database", "Optimize server security benchmarks", "Refactor the global UI styling parameters"],
                "correct_answer_index": 0,
                "explanation": f"The primary goal of this week is explicitly stated as: {week_goal}."
            },
            {
                "question": f"Which technology is most relevant to the weekly practice in Week {week_num}?",
                "options": ["The tools specified in the weekly sequence", "An unrelated database engine", "An old legacy framework", "Browser console logs"],
                "correct_answer_index": 0,
                "explanation": "Aligning your tools with the roadmap objectives ensures high industry readiness."
            },
            {
                "question": "What is the primary benefit of completing this week's mini-project?",
                "options": ["Adding clean portfolio value to your evolving GitHub repository", "Earning certificate credentials without coding", "Completing tasks in a sandbox console", "Skipping prerequisites check"],
                "correct_answer_index": 0,
                "explanation": "JobReady focuses on building an evolving repository to demonstrate real-world contributions."
            },
            {
                "question": "How does the study pace slider affect the weekly curriculum layout?",
                "options": ["It recalculates estimated weeks dynamically based on hours studied", "It changes the order of weekly modules", "It limits the maximum score of quizzes", "It unlocks all badges immediately"],
                "correct_answer_index": 0,
                "explanation": "Selecting a faster pace reduces the completion duration, making study times highly personalized."
            },
            {
                "question": "Which of these best describes the final capstone project?",
                "options": ["A production-grade deployment demonstrating end-to-end readiness", "A short self-assessment quiz", "An isolated coding snippet", "A mock resume outline"],
                "correct_answer_index": 0,
                "explanation": "A Capstone project is a large enterprise-level deployment designed to optimize recruiter interest."
            }
        ]
    }
    
    return fallback_quiz
