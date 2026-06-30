import os
import sys
import json
import asyncio
import httpx
from dotenv import load_dotenv

# Load env variables
dotenv_path = os.path.join("d:\\skillbridge-ai", ".env")
load_dotenv(dotenv_path, override=True)

sys.path.append("d:\\skillbridge-ai")

from google.genai import Client as GeminiClient

ROLES_FILE = "database/roles.json"
RESOURCES_FILE = "database/resources.json"
SKILLS_FILE = "database/skills_network.json"

# =====================================================================
# SECURED API CREDENTIAL LOADING (NO HARDCODED RAW SECRETS)
# =====================================================================
env_primary_gemini = os.environ.get("GEMINI_API_KEY", "").strip()
fallback_raw = os.environ.get("GEMINI_FALLBACK_KEYS", "")

# Dynamically construct the key rotation sequence from the environment parameters
GEMINI_KEYS = []
if env_primary_gemini:
    GEMINI_KEYS.append(env_primary_gemini)

for key in fallback_raw.split(","):
    cleaned_key = key.strip()
    if cleaned_key and cleaned_key not in GEMINI_KEYS:
        GEMINI_KEYS.append(cleaned_key)

if not GEMINI_KEYS:
    print("[WARNING]: Zero active Gemini keys resolved from environmental parameters.")

current_key_idx = 0

# Extract Groq key safely from environment variable configuration
groq_api_key = os.environ.get("GROQ_API_KEY", "").strip()
if not groq_api_key:
    print("[WARNING]: Zero active Groq keys resolved from environmental parameters.")
# =====================================================================

current_engine = "groq-70b"  # Fresh key — zero rate limit history
GEMINI_CLIENTS = {}
# Track Gemini key cooldowns instead of permanently removing them
GEMINI_KEY_COOLDOWN = {}  # key -> timestamp when it becomes available again

def stagger_initial_keys():
    """Pre-cool all keys (assume recent use) then stagger release times 8s apart.
    After 65s, keys become available one every 8s — no simultaneous expiry."""
    import time
    num_keys = len(GEMINI_KEYS)
    if num_keys <= 1:
        return
    now = time.time()
    base_cooldown = 65  # Assume all keys were just used (60s RPM window + 5s buffer)
    release_interval = 8  # Stagger releases 8s apart
    for i, key in enumerate(GEMINI_KEYS):
        # Key i becomes available at: now + base_cooldown + (i * release_interval)
        # Key 0 → available at +65s, Key 1 → +73s, Key 2 → +81s, etc.
        GEMINI_KEY_COOLDOWN[key] = now + base_cooldown + (i * release_interval)
    total_window = base_cooldown + (num_keys - 1) * release_interval
    print(f"[Init]: Pre-cooling {num_keys} Gemini keys. First available in {base_cooldown}s, then 1 every {release_interval}s (total spread: {total_window}s).", flush=True)

def get_available_gemini_key():
    """Return (key, 0) if available, or (None, wait_seconds) if all cooling down."""
    import time
    now = time.time()
    for key in GEMINI_KEYS:
        if GEMINI_KEY_COOLDOWN.get(key, 0) <= now:
            return key, 0
    if not GEMINI_KEYS:
        return None, 0
    # All keys in cooldown - find soonest available
    soonest_key = min(GEMINI_KEYS, key=lambda k: GEMINI_KEY_COOLDOWN.get(k, 0))
    wait = max(0, GEMINI_KEY_COOLDOWN[soonest_key] - now)
    return None, wait

async def query_direct_gemini_async(prompt, api_key):
    """Async Gemini via REST to avoid SSL blocking in asyncio.to_thread."""
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

async def query_llm_batch(batch_roles_data):
    global current_engine, current_key_idx, GEMINI_KEYS
    current_engine = "groq-70b"  # Fresh Groq key — start each batch here
    
    roles_summary = []
    for r_name, r_data in batch_roles_data.items():
        weeks_summary = []
        for wk in r_data.get("weekly_learning_sequence", []):
            weeks_summary.append({
                "week": wk.get("week"),
                "goal": (wk.get("goal") or "")[:80],  # cap at 80 chars
            })
        roles_summary.append({
            "role_name": r_name,
            "domain": r_data.get("domain"),
            "weeks": weeks_summary
        })

    prompt = f"""
    Enrich the following roles with V5.0 educational metadata.
    Roles: {json.dumps(roles_summary, indent=2)}

    For each role in the input, generate a JSON object matching this schema.
    Respond with a JSON object mapping each "role_name" to its metadata:
    {{
      "Role Name 1": {{
        "role_learning_outcomes": [
          "Ability to design and deploy containerized microservices.",
          "Ability to configure automated CI/CD pipelines."
        ],
        "educational_metadata": {{
          "typical_learner_profile": "typical learner profile...",
          "recommended_weekly_study_hours": 12,
          "estimated_completion_time_weeks": 12,
          "difficulty_level": "Beginner/Intermediate/Advanced",
          "industry_readiness_level": "Entry/Mid/Senior Level",
          "portfolio_readiness_score": "High/Medium/Low",
          "recommended_certifications": ["AWS Certified...", "Certified Kubernetes..."],
          "recommended_next_career_paths": ["Next Path 1", "Next Path 2"],
          "common_interview_topics": ["Docker layers", "Git workflow"],
          "common_mistakes_beginners_make": ["Hardcoding credentials", "Skipping container check"]
        }},
        "weekly_learning_sequence": [
          {{
            "week": 1,
            "competencies_gained": [
              {{ "name": "competency name", "mastery_level": "Remember/Understand/Apply/Analyze/Evaluate/Create" }}
            ],
            "concepts_mastered": ["concept 1", "concept 2"],
            "practical_outcomes": "Outcome description",
            "real_world_applications": "Production use case",
            "industry_relevance": "Why industry values this week",
            "project_metadata": {{
              "difficulty": "Beginner/Intermediate/Advanced",
              "estimated_effort": "Low/Medium/High",
              "portfolio_value": "Low/Medium/High",
              "resume_value": "Low/Medium/High",
              "recommended_after": [],
              "prerequisite_projects": []
            }}
          }}
        ],
        "standardized_capstone": {{
          "title": "Capstone Title",
          "problem_statement": "Deploy a multi-tier server grid...",
          "expected_deliverables": ["codebase repository", "Dockerfiles"],
          "deployment_recommendation": "Deploy on AWS or GCP.",
          "github_repository": "capstone-repo-name",
          "readme_requirements": ["Architecture", "Setup instructions"],
          "suggested_resume_bullet": "Designed and deployed a containerized microservice grid, reducing delivery latency by 30%.",
          "suggested_linkedin_project_description": "Built an enterprise-grade containerized FastAPI microservice network featuring Redis caching."
        }}
      }}
    }}

    Rules:
    1. Match the weekly sequence length exactly for each role.
    2. Bloom's Taxonomy mastery level MUST be exactly one of: Remember, Understand, Apply, Analyze, Evaluate, Create.
    3. Keep all text fields (learner profiles, outcomes, real-world apps, relevance, capstone problem statements, resume bullets) extremely concise and compact (e.g. 1-2 short sentences maximum, under 20 words per text property). Do not output verbose descriptions.
    4. Return ONLY raw valid JSON. No markdown code blocks, no backticks.
    """

    retries = 20
    global_wait_count = 0
    while retries > 0:
        try:
            if current_engine == "groq-70b":
                try:
                    response_text = await query_direct_groq(prompt, "llama-3.3-70b-versatile", groq_api_key)
                except Exception as e:
                    if "429" in str(e):
                        print("[System Alert]: Groq 70B rate limited. Falling back to Groq 8B...", flush=True)
                        current_engine = "groq-8b"
                        await asyncio.sleep(15)
                        continue
                    else:
                        raise e
            elif current_engine == "groq-8b":
                try:
                    response_text = await query_direct_groq(prompt, "llama-3.1-8b-instant", groq_api_key)
                except Exception as e:
                    if "429" in str(e):
                        print("[System Alert]: Groq 8B also rate limited. Falling back to Gemini async...", flush=True)
                        current_engine = "gemini"
                        await asyncio.sleep(20)
                        continue
                    else:
                        raise e
            else:  # gemini fallback
                import time
                key, wait_secs = get_available_gemini_key()
                if key is None:
                    # All keys cooling down — wait then switch back to Groq
                    actual_wait = min(wait_secs + 5, 90)
                    global_wait_count += 1
                    print(f"[System Alert]: All Gemini keys cooling down. Waiting {actual_wait:.0f}s then retrying Groq 70B... (global wait #{global_wait_count})", flush=True)
                    await asyncio.sleep(actual_wait)
                    current_engine = "groq-70b"  # Try Groq again after cooldown
                    continue
                try:
                    response_text = await query_direct_gemini_async(prompt, key)
                except httpx.HTTPStatusError as e:
                    err_str = str(e)
                    if "429" in err_str:
                        # Put key in 70s cooldown (RPM window), don't remove permanently
                        cooldown_until = time.time() + 70
                        GEMINI_KEY_COOLDOWN[key] = cooldown_until
                        print(f"[System Alert]: Gemini key {key[:10]}... RPM hit. Cooling down 70s.", flush=True)
                        continue
                    elif "503" in err_str:
                        cooldown_until = time.time() + 30
                        GEMINI_KEY_COOLDOWN[key] = cooldown_until
                        print(f"[System Alert]: Gemini 503. Cooling key 30s.", flush=True)
                        continue
                    else:
                        raise e

                
            # Parse JSON
            cleaned_res = response_text.strip()
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
                
            # Rotate Gemini key on success
            if current_engine == "gemini" and GEMINI_KEYS:
                current_key_idx = (current_key_idx + 1) % len(GEMINI_KEYS)
                
            return json.loads(cleaned_res)
            
        except Exception as ex:
            retries -= 1
            print(f"[ERROR]: Request failed using {current_engine}: {ex}. Retries left: {retries}", flush=True)
            sleep_time = 15
            if "groq" in current_engine:
                err_str = str(ex)
                if "429" in err_str or "rate limit" in err_str.lower():
                    sleep_time = 45
                    print("[System Alert]: Groq hit 429. Sleeping 45s and switching to Gemini...", flush=True)
                    current_engine = "gemini"
                else:
                    print("[System Alert]: Groq failed with non-429. Switching to Gemini...", flush=True)
                    current_engine = "gemini"
            elif current_engine == "gemini":
                print("[System Alert]: Gemini failed. Trying Groq 70B...", flush=True)
                current_engine = "groq-70b"
                sleep_time = 5
            await asyncio.sleep(sleep_time)
            
    raise RuntimeError("Batch failed completely after all engine retries.")

async def enrich_roles():
    stagger_initial_keys()  # Pre-spread keys across 60s window before first request
    if not os.path.exists(ROLES_FILE):
        print(f"[ERROR]: {ROLES_FILE} not found.", flush=True)
        return
        
    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        roles_db = json.load(f)
        
    # Filter roles that need V5 enrichment
    target_roles = {}
    for r_name, r_data in roles_db.items():
        if "role_learning_outcomes" not in r_data or "educational_metadata" not in r_data:
            target_roles[r_name] = r_data
            
    print(f"Total roles needing V5 enrichment: {len(target_roles)}", flush=True)
    if not target_roles:
        print("All roles already enriched under Version 5.0.", flush=True)
        return
        
    # Group into batches of 2
    batch_size = 2
    roles_list = list(target_roles.items())
    batches = [dict(roles_list[i:i+batch_size]) for i in range(0, len(roles_list), batch_size)]
    
    print(f"Processing in {len(batches)} batches of 4 roles...", flush=True)
    
    for idx, batch in enumerate(batches):
        print(f"\nProcessing Batch {idx+1}/{len(batches)}: {list(batch.keys())}", flush=True)
        
        try:
            result_data = await query_llm_batch(batch)
            
            # Merge into roles_db
            for r_name, enrichment in result_data.items():
                matched_name = None
                if r_name in roles_db:
                    matched_name = r_name
                else:
                    for db_name in roles_db.keys():
                        if db_name.lower().strip() == r_name.lower().strip():
                            matched_name = db_name
                            break
                
                if matched_name:
                    roles_db[matched_name]["role_learning_outcomes"] = enrichment.get("role_learning_outcomes", [])
                    roles_db[matched_name]["educational_metadata"] = enrichment.get("educational_metadata", {})
                    roles_db[matched_name]["standardized_capstone"] = enrichment.get("standardized_capstone", {})
                    
                    wk_enrichment = enrichment.get("weekly_learning_sequence", [])
                    for wk_idx, wk_data in enumerate(roles_db[matched_name].get("weekly_learning_sequence", [])):
                        if wk_idx < len(wk_enrichment):
                            enrich_wk = wk_enrichment[wk_idx]
                            wk_data["competencies_gained"] = enrich_wk.get("competencies_gained", [])
                            wk_data["concepts_mastered"] = enrich_wk.get("concepts_mastered", [])
                            wk_data["practical_outcomes"] = enrich_wk.get("practical_outcomes", "")
                            wk_data["real_world_applications"] = enrich_wk.get("real_world_applications", "")
                            wk_data["industry_relevance"] = enrich_wk.get("industry_relevance", "")
                            wk_data["project_metadata"] = enrich_wk.get("project_metadata", {})
                            
            # Save database immediately
            with open(ROLES_FILE, "w", encoding="utf-8") as f:
                json.dump(roles_db, f, indent=2)
                
            print(f"[SUCCESS]: Batch {idx+1} merged successfully!", flush=True)
        except Exception as e:
            print(f"[CRITICAL ERROR]: Batch {idx+1} failed to enrich: {e}. Skipping.", flush=True)
            
        # Cooldown sleep
        if current_engine == "groq-70b":
            await asyncio.sleep(45.0) # Low TPM on Groq 70B
        elif current_engine == "groq-8b":
            await asyncio.sleep(45.0) # Low TPM on Groq 8B
        else:
            await asyncio.sleep(4.0) # Gemini (no TPM limits on free tier, only RPM)

# Automatic metadata extraction for resources
def extract_resources_metadata():
    print("\n--- Extracting Resource Library Metadata ---", flush=True)
    if not os.path.exists(ROLES_FILE):
        print(f"[ERROR]: {ROLES_FILE} not found.", flush=True)
        return
        
    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        roles_db = json.load(f)
        
    resources_db = {}
    if os.path.exists(RESOURCES_FILE):
        try:
            with open(RESOURCES_FILE, "r", encoding="utf-8") as f:
                resources_db = json.load(f)
        except Exception:
            resources_db = {}
            
    print(f"Loaded {len(resources_db)} existing resources from library...", flush=True)
    
    total_added = 0
    for r_name, r_data in roles_db.items():
        weeks = r_data.get("weekly_learning_sequence", [])
        for wk in weeks:
            week_num = wk.get("week", 1)
            resources = wk.get("resources", [])
            for res in resources:
                url = res.get("url")
                if not url:
                    continue
                    
                if url in resources_db and "source_trust" in resources_db[url]:
                    continue
                    
                source_trust = "Community"
                provider_lower = res.get("provider", "").lower()
                url_lower = url.lower()
                
                if any(x in url_lower for x in [".edu", "mit.edu", "stanford.edu", "harvard.edu", "berkeley.edu", "cmu.edu"]):
                    source_trust = "University"
                elif any(x in url_lower for x in ["docs.", "pytorch.org", "docker.com", "fastapi.", "kubernetes.io", "git-scm.com", "prometheus.io", "numpy.org"]):
                    source_trust = "Official"
                elif any(x in provider_lower or x in url_lower for x in ["microsoft", "google", "nvidia", "ibm", "aws", "hugging face", "deeplearning.ai", "fast.ai"]):
                    source_trust = "Industry"
                elif "github.com" in url_lower:
                    source_trust = "Open Source"
                    
                difficulty = "Intermediate"
                if week_num <= 3:
                    difficulty = "Beginner"
                elif week_num >= 9:
                    difficulty = "Advanced"
                    
                estimated_effort = "Medium"
                res_type = res.get("type", "").lower()
                if "course" in res_type or "playlist" in res_type:
                    estimated_effort = "High"
                elif "doc" in res_type or "article" in res_type:
                    estimated_effort = "Medium"
                elif "video" in res_type:
                    estimated_effort = "Low"
                    
                learning_style = "Video"
                if "doc" in res_type or "article" in res_type:
                    learning_style = "Text"
                elif "lab" in res_type or "playground" in res_type:
                    learning_style = "Interactive"
                    
                certification_available = False
                if any(x in provider_lower for x in ["coursera", "microsoft", "google cloud", "nvidia", "udacity"]):
                    certification_available = True
                    
                resources_db[url] = {
                    "title": res.get("title", "Resource"),
                    "provider": res.get("provider", "Unknown"),
                    "type": res.get("type", "video"),
                    "difficulty": difficulty,
                    "estimated_effort": estimated_effort,
                    "free_or_paid": "Free",
                    "source_trust": source_trust,
                    "learning_style": learning_style,
                    "language": "English",
                    "provider_type": res.get("provider", "Platform"),
                    "certification_available": certification_available,
                    "concepts_covered": wk.get("concepts_mastered", ["Core Technologies"]),
                    "prerequisite_skills": [r_name.split(" ")[0]],
                    "learning_outcomes": wk.get("objectives", ["Understand technical principles"]),
                    "tags": [r_data.get("domain", "Technology"), res.get("provider", "Curated")]
                }
                total_added += 1
                
    with open(RESOURCES_FILE, "w", encoding="utf-8") as f:
        json.dump(resources_db, f, indent=2)
        
    print(f"Finished extracting resource library! Total unique resources: {len(resources_db)} (+{total_added} new).", flush=True)

def build_skills_network():
    print("\n--- Constructing Skills Knowledge Graph (skills_network.json) ---", flush=True)
    if not os.path.exists(ROLES_FILE):
        print(f"[ERROR]: {ROLES_FILE} not found.", flush=True)
        return
        
    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        roles_db = json.load(f)
        
    skills_data = {
        # Core Languages
        "Python": {
            "definition": "Core language syntax, data structures, and scripting concepts.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 40,
            "prerequisites": [],
            "next_skills": ["FastAPI", "Machine Learning", "Data Science"]
        },
        "JavaScript": {
            "definition": "Web scripting syntax, DOM operations, ES6 features, and asynchronous execution loops.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 35,
            "prerequisites": [],
            "next_skills": ["TypeScript", "React", "Node.js"]
        },
        "TypeScript": {
            "definition": "Static typing extension for JavaScript, compiler configurations, interfaces, generics, and strict checks.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 20,
            "prerequisites": ["JavaScript"],
            "next_skills": ["React", "Angular", "Next.js"]
        },
        "Go": {
            "definition": "Compiled systems programming language, goroutines concurrency, channels, and strict structural typing.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 30,
            "prerequisites": [],
            "next_skills": ["Docker", "Kubernetes", "gRPC"]
        },
        "Java": {
            "definition": "Object-oriented language compiling to bytecode running on JVM, enterprise designs, and strict hierarchies.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 45,
            "prerequisites": [],
            "next_skills": ["Spring Boot", "Android Development"]
        },
        "C++": {
            "definition": "Low-level system programming language, memory pointers, templates, and performance-critical compilers.",
            "difficulty": "Advanced",
            "estimated_learning_hours": 60,
            "prerequisites": [],
            "next_skills": ["Game Engine Development", "Hardware Drivers"]
        },
        "Rust": {
            "definition": "Safe systems language featuring zero-cost abstractions, borrow checker memory security, and async streams.",
            "difficulty": "Advanced",
            "estimated_learning_hours": 50,
            "prerequisites": [],
            "next_skills": ["WebAssembly", "Safe System Kernels"]
        },
        "HTML/CSS": {
            "definition": "Markup layout structure, responsive grids, flexbox coordinates, animations, and semantic structure.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 20,
            "prerequisites": [],
            "next_skills": ["JavaScript", "Tailwind CSS", "Figma"]
        },
        "SQL": {
            "definition": "Querying relational databases, structuring filters, aggregate grouping, and table joins.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 30,
            "prerequisites": [],
            "next_skills": ["Data Engineering", "PostgreSQL Administration"]
        },
        "Bash Scripting": {
            "definition": "Linux shell script automation, pipe filters, environment properties, and command-line schedules.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 15,
            "prerequisites": [],
            "next_skills": ["Docker", "Linux Shell"]
        },
        "Git": {
            "definition": "Version control systems, commits, branching, merging, and pull request collaborations.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 15,
            "prerequisites": [],
            "next_skills": ["Docker", "CI/CD"]
        },

        # Backend Development
        "FastAPI": {
            "definition": "Building high-performance RESTful APIs, request payloads routing, and data validation via Pydantic.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 25,
            "prerequisites": ["Python", "Git"],
            "next_skills": ["Backend Security", "SaaS Deployments"]
        },
        "Node.js": {
            "definition": "Asynchronous event-driven JavaScript server runtime environment, package registry, and server clustering.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 30,
            "prerequisites": ["JavaScript"],
            "next_skills": ["Express", "GraphQL"]
        },
        "Express": {
            "definition": "Minimalist server routing framework for Node.js, middleware pipelines, and API integrations.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 15,
            "prerequisites": ["Node.js"],
            "next_skills": ["GraphQL", "Microservices"]
        },
        "Django": {
            "definition": "High-level model-view-template Python web framework featuring built-in admin panels and ORM databases.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 35,
            "prerequisites": ["Python"],
            "next_skills": ["Fullstack Web Integration", "SaaS Grid"]
        },
        "Spring Boot": {
            "definition": "Opinionated Java framework for production-grade microservices, dependency injection, and JPA database mapping.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 40,
            "prerequisites": ["Java"],
            "next_skills": ["Enterprise Microservices Grid"]
        },
        "GraphQL": {
            "definition": "Declarative API query language, type definitions schemas, mutations, and server-side resolvers mapping.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 20,
            "prerequisites": ["JavaScript", "REST APIs"],
            "next_skills": ["Apollo Client", "API Gateway Networks"]
        },
        "REST APIs": {
            "definition": "Representational State Transfer network architectures, standard CRUD methods, and HTTP status codes.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 15,
            "prerequisites": [],
            "next_skills": ["FastAPI", "GraphQL", "gRPC"]
        },
        "gRPC": {
            "definition": "High-performance Remote Procedure Call framework using protocol buffers serialization and HTTP/2 channels.",
            "difficulty": "Advanced",
            "estimated_learning_hours": 25,
            "prerequisites": ["Go", "C++", "REST APIs"],
            "next_skills": ["Microservices Coordination"]
        },

        # Frontend Development
        "React": {
            "definition": "Component architecture, virtual DOM updates, useState/useEffect lifecycle hooks, and single-page apps states.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 35,
            "prerequisites": ["HTML/CSS", "JavaScript"],
            "next_skills": ["Next.js", "Fullstack Integration"]
        },
        "Next.js": {
            "definition": "React framework enabling server-side rendering, static generation, API routes, and optimized client layouts.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 25,
            "prerequisites": ["React", "TypeScript"],
            "next_skills": ["Vercel Deployment", "Incremental Static Regeneration"]
        },
        "Tailwind CSS": {
            "definition": "Utility-first CSS framework providing speed classes, responsive configurations, and custom design tokens.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 10,
            "prerequisites": ["HTML/CSS"],
            "next_skills": ["React UI Components"]
        },
        "Vue": {
            "definition": "Progressive JavaScript framework for user interfaces featuring easy directives and reactive virtual DOM.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 30,
            "prerequisites": ["HTML/CSS", "JavaScript"],
            "next_skills": ["Nuxt.js"]
        },
        "Angular": {
            "definition": "Comprehensive enterprise TypeScript framework featuring built-in routers, components, and HTTP client modules.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 40,
            "prerequisites": ["TypeScript"],
            "next_skills": ["RxJS Advanced State Management"]
        },
        "Redux": {
            "definition": "Predictable state container for JavaScript apps featuring centralized store, actions, and reducer functions.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 20,
            "prerequisites": ["React"],
            "next_skills": ["RTK Query"]
        },
        "Webpack": {
            "definition": "JavaScript bundler, asset loaders compilation, source mapping, and production compilation optimizations.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 15,
            "prerequisites": ["JavaScript"],
            "next_skills": ["Vite Speed Configurations"]
        },

        # Data Science / AI / ML
        "Machine Learning": {
            "definition": "Training algorithms on datasets to classify inputs, regress values, or segment clusters.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 40,
            "prerequisites": ["Python", "SQL"],
            "next_skills": ["Deep Learning", "Data Engineering"]
        },
        "Deep Learning": {
            "definition": "Multi-layer artificial neural networks, backpropagation math, gradient descent tuning, and image/text models.",
            "difficulty": "Advanced",
            "estimated_learning_hours": 45,
            "prerequisites": ["Machine Learning"],
            "next_skills": ["NLP", "Computer Vision", "RAG Systems"]
        },
        "PyTorch": {
            "definition": "Tensor computations framework with autograd, custom neural network modules, and GPU model training acceleration.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 30,
            "prerequisites": ["Python", "Machine Learning"],
            "next_skills": ["Deep Learning", "Transformer Tuning"]
        },
        "TensorFlow": {
            "definition": "End-to-end open-source machine learning platform with Keras, computational graphs, and TPU training loops.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 30,
            "prerequisites": ["Python", "Machine Learning"],
            "next_skills": ["Deep Learning", "TF Extended"]
        },
        "Scikit-Learn": {
            "definition": "Python library for classical ML featuring regressions, classification classifiers, preprocessors, and metric evaluation.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 20,
            "prerequisites": ["Python"],
            "next_skills": ["Machine Learning", "Feature Engineering"]
        },
        "Pandas": {
            "definition": "DataFrame manipulation, dataset sorting, data cleaning operations, and aggregate grouping.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 15,
            "prerequisites": ["Python"],
            "next_skills": ["Scikit-Learn", "Data Engineering"]
        },
        "NumPy": {
            "definition": "Multi-dimensional array computations, vectorization operations, linear algebra solvers, and mathematical operations.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 15,
            "prerequisites": ["Python"],
            "next_skills": ["Pandas", "PyTorch"]
        },
        "Data Engineering": {
            "definition": "Building data ingestion pipelines, cleaning batch extracts, orchestrating lake schemas, and relational warehouses.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 40,
            "prerequisites": ["SQL", "Python"],
            "next_skills": ["Apache Spark", "Snowflake"]
        },
        "NLP": {
            "definition": "Natural Language Processing, tokenizers, transformers sentiment, embeddings models, and language understanding.",
            "difficulty": "Advanced",
            "estimated_learning_hours": 35,
            "prerequisites": ["Deep Learning"],
            "next_skills": ["Prompt Engineering", "RAG Systems"]
        },
        "Computer Vision": {
            "definition": "Image preprocessing, convolutional feature extractors, object segmentation, bounding boxes, and video frames tracking.",
            "difficulty": "Advanced",
            "estimated_learning_hours": 35,
            "prerequisites": ["Deep Learning"],
            "next_skills": ["Diffusion Models", "Robotics Navigation"]
        },
        "Prompt Engineering": {
            "definition": "Instructing LLMs via structured context prompts, zero-shot, few-shot, and chain-of-thought system instructions.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 10,
            "prerequisites": [],
            "next_skills": ["RAG Systems", "AI Workflow Engineering"]
        },
        "RAG Systems": {
            "definition": "Retrieval Augmented Generation connecting PDF loaders, text chunk embeds, vector databases, and semantic search queries.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 30,
            "prerequisites": ["Python", "Prompt Engineering"],
            "next_skills": ["Agentic AI", "LLM Evaluation"]
        },
        "Agentic AI": {
            "definition": "Orchestrating stateful autonomous agents, multi-agent networks, decision loops, and tooling execution graphs.",
            "difficulty": "Advanced",
            "estimated_learning_hours": 40,
            "prerequisites": ["Python", "RAG Systems"],
            "next_skills": ["Cognitive Systems Architecture"]
        },
        "Vector Databases": {
            "definition": "Indexing high-dimensional vector embeddings, cosine similarities, HNSW indexes, and metadata filtering.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 15,
            "prerequisites": ["Python"],
            "next_skills": ["RAG Systems"]
        },

        # DevOps / Cloud / Infrastructure
        "Docker": {
            "definition": "Containerization, writing Dockerfiles, mapping port bindings, and managing container storage volumes.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 20,
            "prerequisites": ["Git"],
            "next_skills": ["Kubernetes", "CI/CD"]
        },
        "Kubernetes": {
            "definition": "Fleet orchestration of containers, Kubernetes deployments, service discovery, pod auto-scaling, and grid ingress paths.",
            "difficulty": "Advanced",
            "estimated_learning_hours": 45,
            "prerequisites": ["Docker", "Git"],
            "next_skills": ["Chaos Engineering", "Infrastructure Automation"]
        },
        "CI/CD": {
            "definition": "Continuous integration pipelines, automated container image building, testing suites execution, and cloud deployments.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 20,
            "prerequisites": ["Git", "Docker"],
            "next_skills": ["Platform Engineering"]
        },
        "GitHub Actions": {
            "definition": "Workflow automation triggers, runner execution files, step dependencies, cache actions, and secrets storage security.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 15,
            "prerequisites": ["Git"],
            "next_skills": ["CI/CD"]
        },
        "Terraform": {
            "definition": "Infrastructure as Code (IaC) configuration, cloud providers providers blocks, states management, and modules.",
            "difficulty": "Advanced",
            "estimated_learning_hours": 30,
            "prerequisites": ["AWS", "Git"],
            "next_skills": ["Infrastructure Security Configuration"]
        },
        "AWS": {
            "definition": "Cloud infrastructure administration: EC2 virtualization, S3 storage buckets, IAM permissions, and networking routing.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 30,
            "prerequisites": ["Linux Shell"],
            "next_skills": ["AWS Architecting", "Multicloud Coordination"]
        },
        "Google Cloud Platform": {
            "definition": "Cloud hosting services, App Engine deployments, BigQuery warehouses, and IAM authentication permissions.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 30,
            "prerequisites": ["Linux Shell"],
            "next_skills": ["Multicloud Coordination"]
        },
        "Azure": {
            "definition": "Microsoft cloud ecosystem, Azure Active Directory permissions, Virtual Machines, and Cosmos DB storage databases.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 30,
            "prerequisites": ["Linux Shell"],
            "next_skills": ["Multicloud Coordination"]
        },
        "Ansible": {
            "definition": "Agentless infrastructure configuration automation, playbooks, host inventories configurations, and ssh coordination.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 25,
            "prerequisites": ["Linux Shell"],
            "next_skills": ["Terraform Integration"]
        },
        "Linux Shell": {
            "definition": "CLI operating systems file hierarchies navigation, permissions configuration, processes tracking, and shell pipes.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 15,
            "prerequisites": [],
            "next_skills": ["Bash Scripting", "AWS"]
        },
        "Nginx": {
            "definition": "Reverse proxy web servers hosting routing setups, load balancer coordination, and SSL certificate mappings.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 15,
            "prerequisites": ["Linux Shell"],
            "next_skills": ["API Gateways"]
        },
        "Prometheus": {
            "definition": "Time series database monitoring systems collecting CPU/RAM metrics and alert configurations.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 20,
            "prerequisites": ["Docker"],
            "next_skills": ["Grafana Dashboards"]
        },
        "Grafana": {
            "definition": "Analytics dashboards charting metrics visualizations, connecting data interfaces, and creating alerts panels.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 15,
            "prerequisites": ["Prometheus"],
            "next_skills": ["SRE Dashboards"]
        },

        # Mobile / Desktop
        "Swift": {
            "definition": "Apple native applications compiled language, memory management safety, and UIKit/SwiftUI layout components.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 35,
            "prerequisites": [],
            "next_skills": ["SwiftUI Development"]
        },
        "Kotlin": {
            "definition": "Modern JVM language, Android applications, coroutines, and null safety architectures.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 35,
            "prerequisites": ["Java"],
            "next_skills": ["Android SDK Architectures"]
        },
        "Flutter": {
            "definition": "Cross-platform mobile SDK using Dart compiler engine, canvas layouts, and widget state trees.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 30,
            "prerequisites": [],
            "next_skills": ["Cross-platform Capstone Deployments"]
        },
        "React Native": {
            "definition": "JavaScript framework leveraging React component structure to render native iOS and Android apps views.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 30,
            "prerequisites": ["React"],
            "next_skills": ["Native Bridge Modules"]
        },

        # Security / Testing
        "Cybersecurity": {
            "definition": "Infrastructure security configuration protocols, network firewalls setup, cryptography algorithms, and auth designs.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 40,
            "prerequisites": ["Linux Shell"],
            "next_skills": ["Penetration Testing"]
        },
        "Penetration Testing": {
            "definition": "Ethical hacking exploits testing, finding open network vulnerabilities, SQL injections, and system exploits.",
            "difficulty": "Advanced",
            "estimated_learning_hours": 45,
            "prerequisites": ["Cybersecurity"],
            "next_skills": ["Red Team Infrastructure Testing"]
        },
        "Unit Testing": {
            "definition": "Writing testing assertions validating single modules functions isolation, mock classes, and coverage reports.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 15,
            "prerequisites": ["Python", "JavaScript", "Java"],
            "next_skills": ["CI/CD"]
        },

        # UI/UX / Design
        "UI/UX Design": {
            "definition": "Visual UI hierarchies layouts creation, color coordinate theories, user pathways mapping, and interface wireframing.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 25,
            "prerequisites": [],
            "next_skills": ["Figma", "Design Systems"]
        },
        "Figma": {
            "definition": "Designing responsive app wireframes, component design libraries, interaction triggers, and user layouts mockups.",
            "difficulty": "Beginner",
            "estimated_learning_hours": 15,
            "prerequisites": [],
            "next_skills": ["Product Design", "Figma-to-Code Developer"]
        },

        # Data Management / Databases
        "PostgreSQL": {
            "definition": "Relational database server, indexes operations, query optimization, connection pools, and transactional isolation.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 30,
            "prerequisites": ["SQL"],
            "next_skills": ["Database Administration"]
        },
        "MongoDB": {
            "definition": "NoSQL document database storage storing JSON documents, dynamic schemas configurations, and aggregate arrays queries.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 20,
            "prerequisites": [],
            "next_skills": ["Scaling NoSQL Grids"]
        },
        "Redis": {
            "definition": "In-memory database cache, key-value storage grids, publish-subscribe queues, and atomic operations.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 15,
            "prerequisites": [],
            "next_skills": ["High Performance Caching Grid Architecture"]
        },
        "Cassandra": {
            "definition": "Distributed wide-column storage database scaling huge write loops across cluster rings.",
            "difficulty": "Advanced",
            "estimated_learning_hours": 35,
            "prerequisites": ["SQL"],
            "next_skills": ["Big Data Infrastructure"]
        },
        "Scale Compute (Spark)": {
            "definition": "Cluster data compute framework processing large batch records, dataset transforms, and RDD pools.",
            "difficulty": "Advanced",
            "estimated_learning_hours": 40,
            "prerequisites": ["Python", "SQL"],
            "next_skills": ["PySpark Machine Learning Pipeline"]
        },
        "PySpark": {
            "definition": "Python wrapper interface API connecting to Apache Spark cluster compute grids, mapping datasets dataframes.",
            "difficulty": "Advanced",
            "estimated_learning_hours": 30,
            "prerequisites": ["Python", "Scale Compute (Spark)"],
            "next_skills": ["Big Data Analytics"]
        },
        "Snowflake": {
            "definition": "Cloud data warehousing system, cloud storage separation, SQL analysis scaling, and pipelines.",
            "difficulty": "Intermediate",
            "estimated_learning_hours": 25,
            "prerequisites": ["SQL"],
            "next_skills": ["Enterprise Business Intelligence Pipelines"]
        },
        "Apache Kafka": {
            "definition": "Distributed event streaming platform, message topic partition queues, producers and consumers loops.",
            "difficulty": "Advanced",
            "estimated_learning_hours": 35,
            "prerequisites": ["Docker"]
        }
    }
    
    for skill_name, skill_info in skills_data.items():
        career_roles_using_skill = []
        projects_using_skill = []
        
        skill_info["related_skills"] = []
        if "Python" in skill_name or skill_name in ["SQL", "Git"]:
            skill_info["related_skills"] = ["Python", "SQL", "Git"]
        elif skill_name in ["Docker", "Kubernetes", "CI/CD"]:
            skill_info["related_skills"] = ["Docker", "Kubernetes", "CI/CD"]
        else:
            skill_info["related_skills"] = ["REST APIs", "Git"]
            
        for r_name, r_data in roles_db.items():
            tech_used = [t.lower() for t in r_data.get("technologies_used", [])]
            overview = r_data.get("role_overview", "").lower()
            
            if skill_name.lower() in tech_used or skill_name.lower() in r_name.lower() or skill_name.lower() in overview:
                career_roles_using_skill.append(r_name)
                
            weeks = r_data.get("weekly_learning_sequence", [])
            for wk in weeks:
                project_desc = wk.get("project", "")
                artifact = wk.get("github_portfolio_artifact", "")
                if skill_name.lower() in project_desc.lower() or skill_name.lower() in artifact.lower():
                    if artifact and artifact not in projects_using_skill:
                        projects_using_skill.append(artifact)
                        
        skill_info["career_roles_using_skill"] = career_roles_using_skill[:15]
        skill_info["projects_using_skill"] = projects_using_skill[:10]
        skill_info["concept_dependencies"] = {
            "Variables": "prerequisite for Lists & Dicts",
            "Functions": "prerequisite for OOP & Classes",
            "Fundamentals": "prerequisite for Advanced Operations",
            "Tool Setup": "prerequisite for API Integration"
        }
        
    with open(SKILLS_FILE, "w", encoding="utf-8") as f:
        json.dump(skills_data, f, indent=2)
        
    print(f"Finished constructing skills network! Generated {len(skills_data)} canonical tech skills.", flush=True)

async def main():
    print("=== Starting Version 5.0 Seeding Phase ===", flush=True)
    await enrich_roles()
    extract_resources_metadata()
    build_skills_network()
    print("=== Seeding Phase Complete ===", flush=True)

if __name__ == "__main__":
    asyncio.run(main())