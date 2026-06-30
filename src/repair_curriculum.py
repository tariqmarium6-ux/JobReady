import os
import sys
import json
import asyncio
import httpx
import time
from dotenv import load_dotenv

# Load env variables
dotenv_path = os.path.join("d:\\skillbridge-ai", ".env")
load_dotenv(dotenv_path, override=True)

sys.path.append("d:\\skillbridge-ai")

ROLES_FILE = "database/roles.json"

# 1. Dynamically read primary key and fallback rotation keys from the environment
env_primary_gemini = os.environ.get("GEMINI_API_KEY", "").strip()
fallback_raw = os.environ.get("GEMINI_FALLBACK_KEYS", "")

# Rebuild the key list using environment lookups safely
GEMINI_KEYS = []
if env_primary_gemini:
    GEMINI_KEYS.append(env_primary_gemini)

# Append any fallback keys found in the comma-separated environment variable
for key in fallback_raw.split(","):
    cleaned_key = key.strip()
    if cleaned_key and cleaned_key not in GEMINI_KEYS:
        GEMINI_KEYS.append(cleaned_key)

# Fallback block if absolutely nothing is loaded in environment
if not GEMINI_KEYS:
    print("[WARNING]: No Gemini API keys found in environment variables.")

current_key_idx = 0

# 2. Extract Groq key safely from environment variable instead of plain text string
groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()
if not groq_api_key:
    print("[WARNING]: No Groq API key found in environment variables.")

current_engine = "groq-70b"
GEMINI_KEY_COOLDOWN = {}

def get_available_gemini_key():
    now = time.time()
    for key in GEMINI_KEYS:
        if GEMINI_KEY_COOLDOWN.get(key, 0) <= now:
            return key, 0
    if not GEMINI_KEYS:
        return None, 0
    soonest_key = min(GEMINI_KEYS, key=lambda k: GEMINI_KEY_COOLDOWN.get(k, 0))
    wait = max(0, GEMINI_KEY_COOLDOWN[soonest_key] - now)
    return None, wait

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

async def query_llm(prompt):
    global current_engine, current_key_idx
    retries = 10
    while retries > 0:
        try:
            if current_engine == "groq-70b":
                try:
                    return await query_direct_groq(prompt, "llama-3.3-70b-versatile", groq_api_key)
                except Exception as e:
                    if "429" in str(e):
                        print("[System Alert]: Groq 70B rate limited. Falling back to Groq 8B...", flush=True)
                        current_engine = "groq-8b"
                        await asyncio.sleep(15)
                        continue
                    raise e
            elif current_engine == "groq-8b":
                try:
                    return await query_direct_groq(prompt, "llama-3.1-8b-instant", groq_api_key)
                except Exception as e:
                    if "429" in str(e):
                        print("[System Alert]: Groq 8B rate limited. Falling back to Gemini async...", flush=True)
                        current_engine = "gemini"
                        await asyncio.sleep(20)
                        continue
                    raise e
            else:  # gemini
                key, wait_secs = get_available_gemini_key()
                if key is None:
                    actual_wait = min(wait_secs + 5, 90)
                    print(f"[System Alert]: All Gemini keys cooling down. Waiting {actual_wait:.0f}s then retrying Groq 70B...", flush=True)
                    await asyncio.sleep(actual_wait)
                    current_engine = "groq-70b"
                    continue
                try:
                    return await query_direct_gemini_async(prompt, key)
                except httpx.HTTPStatusError as e:
                    if "429" in str(e):
                        GEMINI_KEY_COOLDOWN[key] = time.time() + 70
                        print(f"[System Alert]: Gemini key {key[:10]}... RPM hit. Cooling down 70s.", flush=True)
                        continue
                    elif "503" in str(e):
                        GEMINI_KEY_COOLDOWN[key] = time.time() + 30
                        print(f"[System Alert]: Gemini 503. Cooling key 30s.", flush=True)
                        continue
                    raise e
        except Exception as ex:
            retries -= 1
            print(f"[ERROR]: Request failed using {current_engine}: {ex}. Retries left: {retries}", flush=True)
            await asyncio.sleep(10)
    raise RuntimeError("Query failed after all retries.")

def repair_bloom_levels(roles_db):
    bloom_map = {
        "u": "Understand", "understand": "Understand",
        "a": "Apply", "apply": "Apply",
        "e": "Evaluate", "evaluate": "Evaluate",
        "c": "Create", "create": "Create",
        "r": "Remember", "remember": "Remember",
        "an": "Analyze", "analyze": "Analyze"
    }
    corrected = 0
    for role_name, role_data in roles_db.items():
        weeks = role_data.get("weekly_learning_sequence", [])
        for wk in weeks:
            comp = wk.get("competencies_gained", [])
            for c in comp:
                lvl = c.get("mastery_level")
                if lvl:
                    cleaned_lvl = str(lvl).strip().lower()
                    if cleaned_lvl in bloom_map:
                        new_lvl = bloom_map[cleaned_lvl]
                        if new_lvl != lvl:
                            c["mastery_level"] = new_lvl
                            corrected += 1
    print(f"Corrected {corrected} invalid Bloom's Taxonomy mastery levels in local DB.", flush=True)

async def main():
    if not os.path.exists(ROLES_FILE):
        print(f"[ERROR]: {ROLES_FILE} not found.", flush=True)
        return

    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        roles_db = json.load(f)

    # 1. Clean up Bloom levels immediately
    repair_bloom_levels(roles_db)

    # 2. Find missing weeks per role
    missing_w = {}
    for r_name, r_data in roles_db.items():
        weeks = r_data.get("weekly_learning_sequence", [])
        missing = []
        for wk in weeks:
            week_num = wk.get("week")
            v5_present = all(f in wk for f in ["competencies_gained", "concepts_mastered", "practical_outcomes", "real_world_applications", "industry_relevance"])
            if not v5_present:
                missing.append(wk)
        if missing:
            missing_w[r_name] = missing

    print(f"Total roles needing week-level V5 repair: {len(missing_w)}", flush=True)
    if not missing_w:
        print("No missing weeks detected. Saving corrected Bloom levels.", flush=True)
        with open(ROLES_FILE, "w", encoding="utf-8") as f:
            json.dump(roles_db, f, indent=2)
        return

    for idx, (role_name, missing_weeks) in enumerate(missing_w.items()):
        print(f"\n[{idx+1}/{len(missing_w)}] Repairing role '{role_name}' ({len(missing_weeks)} weeks missing)...", flush=True)
        
        # Prepare context for the prompt
        weeks_context = []
        for wk in missing_weeks:
            weeks_context.append({
                "week": wk.get("week"),
                "goal": (wk.get("goal") or "")[:80]
            })

        prompt = f"""
        Provide V5.0 educational metadata for the following weeks of the role '{role_name}'.
        Weeks: {json.dumps(weeks_context, indent=2)}

        For each week listed above, respond with a JSON object matching this schema.
        Respond with a JSON object mapping each "week" number (as string) to its metadata:
        {{
          "1": {{
            "competencies_gained": [
              {{ "name": "competency name", "mastery_level": "Remember/Understand/Apply/Analyze/Evaluate/Create" }}
            ],
            "concepts_mastered": ["concept 1", "concept 2"],
            "practical_outcomes": "Outcome description (concise)",
            "real_world_applications": "Production use case (concise)",
            "industry_relevance": "Why industry values this week (concise)",
            "project_metadata": {{
              "difficulty": "Beginner/Intermediate/Advanced",
              "estimated_effort": "Low/Medium/High",
              "portfolio_value": "Low/Medium/High",
              "resume_value": "Low/Medium/High",
              "recommended_after": [],
              "prerequisite_projects": []
            }}
          }}
        }}

        Rules:
        1. Bloom's Taxonomy mastery level MUST be exactly one of: Remember, Understand, Apply, Analyze, Evaluate, Create.
        2. Keep all text fields under 20 words maximum. Be extremely concise.
        3. Return ONLY valid raw JSON. No markdown backticks or wrappers.
        4. """

        try:
            res_text = await query_llm(prompt)
            # Clean up potential markdown wrapper
            cleaned_res = res_text.strip()
            if cleaned_res.startswith("```"):
                lines = cleaned_res.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned_res = "\n".join(lines).strip()

            start_idx = cleaned_res.find("{")
            end_idx = cleaned_res.rfind("}") + 1
            if start_idx != -1 and end_idx != -1:
                cleaned_res = cleaned_res[start_idx:end_idx]

            enrichment_data = json.loads(cleaned_res)

            # Merge into roles_db
            weeks = roles_db[role_name].get("weekly_learning_sequence", [])
            for wk in weeks:
                week_num_str = str(wk.get("week"))
                if week_num_str in enrichment_data:
                    enrich = enrichment_data[week_num_str]
                    wk["competencies_gained"] = enrich.get("competencies_gained", [])
                    wk["concepts_mastered"] = enrich.get("concepts_mastered", [])
                    wk["practical_outcomes"] = enrich.get("practical_outcomes", "")
                    wk["real_world_applications"] = enrich.get("real_world_applications", "")
                    wk["industry_relevance"] = enrich.get("industry_relevance", "")
                    wk["project_metadata"] = enrich.get("project_metadata", {})

            # Repair Bloom levels of newly generated entries just in case
            repair_bloom_levels(roles_db)

            # Save database immediately
            with open(ROLES_FILE, "w", encoding="utf-8") as f:
                json.dump(roles_db, f, indent=2)

            print(f"[SUCCESS]: Role '{role_name}' repaired successfully!", flush=True)

        except Exception as e:
            print(f"[CRITICAL ERROR]: Failed to repair role '{role_name}': {e}. Skipping.", flush=True)

        # Brief cooldown between queries to prevent aggressive rate limits
        if "groq" in current_engine:
            await asyncio.sleep(20.0)
        else:
            await asyncio.sleep(3.0)

    print("\n=== Repair Complete ===", flush=True)

if __name__ == "__main__":
    asyncio.run(main())