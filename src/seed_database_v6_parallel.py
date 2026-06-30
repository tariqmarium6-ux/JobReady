import os
import sys
import json
import asyncio
import httpx
import time
import urllib.parse
from dotenv import load_dotenv

# Load env variables
dotenv_path = os.path.join("d:\\skillbridge-ai", ".env")
load_dotenv(dotenv_path, override=True)

sys.path.append("d:\\skillbridge-ai")

# Re-seed the baseline V4 database first
from src.seed_database import seed as seed_v4
print("Recreating baseline V4 database...", flush=True)
seed_v4()

ROLES_FILE = "database/roles.json"

# =====================================================================
# SECURED API CREDENTIAL LOADING (NO HARDCODED RAW SECRETS)
# =====================================================================
env_primary_gemini = os.environ.get("GEMINI_API_KEY", "").strip()
fallback_raw = os.environ.get("GEMINI_FALLBACK_KEYS", "")

# Rebuild the key pool dynamically using clean environment lookups
GEMINI_KEYS = []
if env_primary_gemini:
    GEMINI_KEYS.append(env_primary_gemini)

for key in fallback_raw.split(","):
    cleaned_key = key.strip()
    if cleaned_key and cleaned_key not in GEMINI_KEYS:
        GEMINI_KEYS.append(cleaned_key)

if not GEMINI_KEYS:
    print("[WARNING]: No active Gemini keys resolved from environmental parameters.")

current_key_idx = 0

# Extract Groq API Key safely from your environment configuration 
groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()
if not groq_api_key:
    print("[WARNING]: No active Groq key resolved from environmental parameters.")
# =====================================================================

current_engine = "groq-70b"
GEMINI_KEY_COOLDOWN = {key: 0.0 for key in GEMINI_KEYS}

# High-trust and medium-trust domains for resource confidence
high_trust = [
    "stanford.edu", "mit.edu", "harvard.edu", "berkeley.edu", "cmu.edu",
    "python.org", "docker.com", "pytorch.org", "tensorflow.org", "kubernetes.io",
    "github.com", "microsoft.com", "google.com", "aws.amazon.com", "redhat.com",
    "owasp.org", "cncf.io", "linuxfoundation.org", "deeplearning.ai", "nvidia.com",
    "openai.com", "huggingface.co", "freecodecamp.org"
]
medium_trust = ["youtube.com", "youtu.be", "coursera.org", "udemy.com", "medium.com", "dev.to"]

# Career difficulty mapping
ROLE_DIFFICULTY = {
    # Advanced Roles
    "Penetration Tester": ("Advanced", 400),
    "Machine Learning Engineer": ("Advanced", 450),
    "Cloud Solutions Architect": ("Advanced", 400),
    "Site Reliability Engineer": ("Advanced", 380),
    "Deep Learning Engineer": ("Advanced", 450),
    "NLP Engineer": ("Advanced", 400),
    "Computer Vision Architect": ("Advanced", 400),
    "Cybersecurity Engineer": ("Advanced", 360),
    "Data Scientist": ("Advanced", 380),
    "AI Specialist": ("Advanced", 420),
    "AI Researcher": ("Advanced", 480),
    "Cognitive Systems Architect": ("Advanced", 450),
    "AI Solutions Engineer": ("Advanced", 380),
    # Intermediate Roles
    "Backend Engineer": ("Intermediate", 240),
    "Frontend Engineer": ("Beginner", 180),
    "Full Stack Developer": ("Intermediate", 320),
    "DevOps Engineer": ("Intermediate", 280),
    "Data Pipeline Engineer": ("Intermediate", 260),
    "iOS Developer": ("Intermediate", 280),
    "Android Developer": ("Intermediate", 280)
}

ROLE_PREREQS = {
    "Penetration Tester": [
        {"role_name": "Git", "domain": "Software Engineering"},
        {"role_name": "Git Operations Lead", "domain": "Software Engineering"}
    ],
    "Machine Learning Engineer": [
        {"role_name": "Python Server Developer", "domain": "Backend Development"},
        {"role_name": "Data Analyst", "domain": "Data Analytics"}
    ],
    "Cloud Solutions Architect": [
        {"role_name": "Systems Engineer", "domain": "Software Engineering"},
        {"role_name": "Cloud Systems Administrator", "domain": "Cloud Computing"}
    ],
    "Full Stack Developer": [
        {"role_name": "Frontend Developer", "domain": "Software Engineering"},
        {"role_name": "Backend Developer", "domain": "Software Engineering"}
    ],
    "Data Scientist": [
        {"role_name": "Data Analyst", "domain": "Data Analytics"},
        {"role_name": "Python Server Developer", "domain": "Backend Development"}
    ]
}

def get_available_key():
    now = time.time()
    for key in GEMINI_KEYS:
        if GEMINI_KEY_COOLDOWN[key] <= now:
            return key
    if not GEMINI_KEYS:
        return None
    best_key = min(GEMINI_KEYS, key=lambda k: GEMINI_KEY_COOLDOWN[k])
    return best_key

async def query_direct_gemini_async(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
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
                "content": "You are an expert university curriculum editor. Respond strictly with valid JSON."
            },
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        res = await client.post(url, json=payload, headers=headers)
        if res.status_code == 429:
            raise httpx.HTTPStatusError("429 Rate Limit Exceeded", request=res.request, response=res)
        if res.status_code in (400, 413):
            raise httpx.HTTPStatusError(f"{res.status_code} Payload Too Large", request=res.request, response=res)
        res.raise_for_status()
        res_json = res.json()
        return res_json["choices"][0]["message"]["content"]

async def query_llm_v6(prompt):
    global current_engine
    retries = 15
    while retries > 0:
        try:
            if current_engine == "groq-70b":
                try:
                    return await query_direct_groq(prompt, "llama-3.3-70b-versatile", groq_api_key)
                except Exception as e:
                    if "429" in str(e):
                        print("[System Alert]: Groq 70B rate limited. Falling back to Groq 8B...", flush=True)
                        current_engine = "groq-8b"
                        await asyncio.sleep(8)
                        continue
                    raise e
            elif current_engine == "groq-8b":
                try:
                    return await query_direct_groq(prompt, "llama-3.1-8b-instant", groq_api_key)
                except Exception as e:
                    if "429" in str(e):
                        print("[System Alert]: Groq 8B rate limited. Falling back to Gemini...", flush=True)
                        current_engine = "gemini"
                        await asyncio.sleep(12)
                        continue
                    raise e
            else:  # gemini
                key = get_available_key()
                if not key:
                    current_engine = "groq-70b"
                    await asyncio.sleep(5)
                    continue
                now = time.time()
                wait_time = GEMINI_KEY_COOLDOWN[key] - now
                if wait_time > 0:
                    await asyncio.sleep(min(wait_time, 5))
                    continue
                try:
                    res = await query_direct_gemini_async(prompt, key)
                    GEMINI_KEY_COOLDOWN[key] = time.time() + 6.0 # rate limiting buffer
                    return res
                except httpx.HTTPStatusError as e:
                    if "429" in str(e):
                        GEMINI_KEY_COOLDOWN[key] = time.time() + 65.0
                        print(f"[System Alert]: Gemini key {key[:10]} RPM hit. Cooling 65s.", flush=True)
                        continue
                    elif "503" in str(e):
                        GEMINI_KEY_COOLDOWN[key] = time.time() + 30.0
                        continue
                    raise e
        except Exception as ex:
            retries -= 1
            print(f"[ERROR]: Retry failed inside LLM dispatcher: {ex}. Retries left: {retries}", flush=True)
            await asyncio.sleep(4)
            current_engine = "groq-70b"
            
    raise RuntimeError("Query failed after all retries.")

def inject_confidence(weeks_list):
    for wk in weeks_list:
        for res in wk.get("resources", []):
            url = res.get("url", "")
            prov = str(res.get("provider", "")).lower()
            conf = "Needs Review"
            try:
                netloc = urllib.parse.urlparse(url).netloc.lower()
                if any(d in netloc for d in high_trust):
                    conf = "High"
                elif any(d in netloc for d in medium_trust):
                    conf = "Medium"
                if any(p in prov for p in ["stanford", "mit ", "harvard", "official", "pytorch", "hugging face", "openai"]):
                    conf = "High"
            except Exception:
                pass
            res["confidence"] = conf

async def enrich_role_task(role_name, role_data, sem):
    async with sem:
        tier, hours = ROLE_DIFFICULTY.get(role_name, ("Intermediate", 240))
        weeks = role_data.get("weekly_learning_sequence", [])
        
        # Build prompt
        weeks_summary = []
        for wk in weeks:
            weeks_summary.append({
                "week": wk.get("week"),
                "goal": (wk.get("goal") or "")[:80]
            })
            
        prompt = f"""
        You are a senior technical curriculum editor. Enrich the career roadmap for '{role_name}' into the Version 6.0 standard.
        Difficulty Tier: {tier} | Total estimated hours: {hours}
        Syllabus Weeks: {json.dumps(weeks_summary, indent=2)}

        Provide a JSON object containing the V6.0 metadata fields:
        {{
          "role_difficulty_tier": "{tier}",
          "estimated_learning_hours": {hours},
          "exit_outcomes": [
            "Exit competency 1 (under 10 words)",
            "Exit competency 2 (under 10 words)",
            "Exit competency 3 (under 10 words)"
          ],
          "specialization_branches": [
            {{
              "branch_name": "Specialization track name",
              "description": "Short track description."
            }}
          ],
          "weekly_learning_sequence": [
            {{
              "week": 1,
              "why_this_week_exists": "A brief mentor note explaining why this week's topic is positioned here.",
              "weekly_time_breakdown": {{
                "total_hours": 12,
                "video_hours": 3,
                "lab_hours": 5,
                "project_hours": 4
              }},
              "practice": "Upgraded practice lab details referencing actual platforms (TryHackMe, PortSwigger, HTB, PicoCTF, etc.) where appropriate.",
              "project": "Upgraded mini project. Ensure it builds on the previous week's codebase inside the evolving repository.",
              "evolving_repository_name": "evolving-github-repo-name",
              "checkpoint": {{
                "type": "Scenario-Based/Debugging/Interview/Decision-Making",
                "question": "Scenario or technical interview question verifying this week's outcomes.",
                "correct_reasoning": "Detailed technical reasoning explaining the correct answer."
              }}
            }}
          ],
          "standardized_capstone": {{
            "title": "Enterprise deployment capstone title",
            "problem_statement": "Describe a large enterprise problem.",
            "expected_deliverables": ["Deliverable 1", "Deliverable 2"],
            "deployment_recommendation": "AWS/GCP/etc.",
            "github_repository": "capstone-repo-name",
            "readme_requirements": ["Setup guide", "Architecture diag"],
            "suggested_resume_bullet": "Resume action bullet.",
            "suggested_linkedin_project_description": "LinkedIn description."
          }}
        }}

        Rules:
        1. Keep all text fields short and high-impact.
        2. Match weekly sequence length exactly ({len(weeks)} weeks).
        3. Do NOT include markdown code blocks, just raw JSON.
        """
        
        try:
            res_text = await query_llm_v6(prompt)
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
                
            enrichment = json.loads(cleaned)
            
            # Merge
            role_data["role_difficulty_tier"] = enrichment.get("role_difficulty_tier", tier)
            role_data["estimated_learning_hours"] = enrichment.get("estimated_learning_hours", hours)
            role_data["role_prerequisites"] = ROLE_PREREQS.get(role_name, [])
            role_data["exit_outcomes"] = enrichment.get("exit_outcomes", [])
            role_data["specialization_branches"] = enrichment.get("specialization_branches", [])
            role_data["standardized_capstone"] = enrichment.get("standardized_capstone", {})
            
            enrich_weeks = enrichment.get("weekly_learning_sequence", [])
            db_weeks = role_data.get("weekly_learning_sequence", [])
            
            for w_idx, wk in enumerate(db_weeks):
                if w_idx < len(enrich_weeks):
                    ew = enrich_weeks[w_idx]
                    wk["why_this_week_exists"] = ew.get("why_this_week_exists", "")
                    wk["weekly_time_breakdown"] = ew.get("weekly_time_breakdown", {
                        "total_hours": 12, "video_hours": 3, "lab_hours": 5, "project_hours": 4
                    })
                    wk["practice"] = ew.get("practice", wk.get("practice", ""))
                    wk["project"] = ew.get("project", wk.get("project", ""))
                    wk["evolving_repository_name"] = ew.get("evolving_repository_name", "")
                    wk["checkpoint_v6"] = ew.get("checkpoint", {})
            
            inject_confidence(db_weeks)
            print(f"[SUCCESS]: Enriched '{role_name}'", flush=True)
        except Exception as e:
            print(f"[ERROR]: Failed to enrich '{role_name}': {e}", flush=True)

async def main():
    if not os.path.exists(ROLES_FILE):
        print(f"[ERROR]: {ROLES_FILE} not found.", flush=True)
        return
        
    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        roles_db = json.load(f)
        
    # Process 4 requests in parallel to stay safely within Groq RPM and Gemini concurrency limits
    sem = asyncio.Semaphore(4)
    
    tasks = []
    for role_name, role_data in roles_db.items():
        tasks.append(enrich_role_task(role_name, role_data, sem))
        
    print(f"Starting parallel V6 enrichment for {len(tasks)} roles...", flush=True)
    start_time = time.time()
    await asyncio.gather(*tasks)
    
    # Save the fully enriched database
    with open(ROLES_FILE, "w", encoding="utf-8") as f:
        json.dump(roles_db, f, indent=2)
        
    duration = time.time() - start_time
    print(f"=== Parallel Enrichment Complete in {duration:.1f}s ===", flush=True)

if __name__ == "__main__":
    asyncio.run(main())