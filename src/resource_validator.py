import os
import json
from datetime import datetime
try:
    from src.ai_fallback_helper import generate_emergency_resource
except ModuleNotFoundError:
    from ai_fallback_helper import generate_emergency_resource

STATUS_FILE = "database/resource_status.json"
RESOURCES_FILE = "database/resources.json"

FALLBACK_REGISTRY = {
    "python": [
        {
            "title": "Python Tutorial for Beginners [Full Course]",
            "provider": "Programming with Mosh",
            "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
            "type": "video",
            "trust_score": 9.8,
            "educational_quality": "Excellent",
            "difficulty": "Beginner",
            "estimated_duration": "6 hrs",
            "provider_type": "Community"
        },
        {
            "title": "Python for Beginners - Full Course",
            "provider": "freeCodeCamp",
            "url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
            "type": "video",
            "trust_score": 9.9,
            "educational_quality": "Excellent",
            "difficulty": "Beginner",
            "estimated_duration": "4 hrs",
            "provider_type": "Community"
        },
        {
            "title": "Python Tutorial Documentation",
            "provider": "Python Docs",
            "url": "https://docs.python.org/3/tutorial/",
            "type": "Documentation",
            "trust_score": 10.0,
            "educational_quality": "Excellent",
            "difficulty": "Beginner",
            "estimated_duration": "Self-paced",
            "provider_type": "Official Docs"
        }
    ],
    "sql": [
        {
            "title": "SQL Tutorial for Beginners",
            "provider": "Programming with Mosh",
            "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
            "type": "video",
            "trust_score": 9.7,
            "educational_quality": "Excellent",
            "difficulty": "Beginner",
            "estimated_duration": "3 hrs",
            "provider_type": "Community"
        },
        {
            "title": "PostgreSQL Tutorial Core Guide",
            "provider": "PostgreSQL Tutorial",
            "url": "https://www.postgresqltutorial.com/",
            "type": "Documentation",
            "trust_score": 9.9,
            "educational_quality": "Excellent",
            "difficulty": "Beginner",
            "estimated_duration": "Self-paced",
            "provider_type": "Official Docs"
        }
    ],
    "docker": [
        {
            "title": "Docker Tutorial for Beginners",
            "provider": "Programming with Mosh",
            "url": "https://www.youtube.com/watch?v=pTFZFxd4hOI",
            "type": "video",
            "trust_score": 9.8,
            "educational_quality": "Excellent",
            "difficulty": "Beginner",
            "estimated_duration": "2 hrs",
            "provider_type": "Community"
        },
        {
            "title": "Docker Documentation Guides",
            "provider": "Docker Docs",
            "url": "https://docs.docker.com/get-started/",
            "type": "Documentation",
            "trust_score": 10.0,
            "educational_quality": "Excellent",
            "difficulty": "Beginner",
            "estimated_duration": "Self-paced",
            "provider_type": "Official Docs"
        }
    ],
    "git": [
        {
            "title": "Git and GitHub for Beginners",
            "provider": "freeCodeCamp",
            "url": "https://www.youtube.com/watch?v=RGOj5yH7evk",
            "type": "video",
            "trust_score": 9.8,
            "educational_quality": "Excellent",
            "difficulty": "Beginner",
            "estimated_duration": "1 hr",
            "provider_type": "Community"
        },
        {
            "title": "Git Reference Documentation",
            "provider": "Git Docs",
            "url": "https://git-scm.com/doc",
            "type": "Documentation",
            "trust_score": 10.0,
            "educational_quality": "Excellent",
            "difficulty": "Beginner",
            "estimated_duration": "Self-paced",
            "provider_type": "Official Docs"
        }
    ],
    "llm": [
        {
            "title": "Intro to Large Language Models",
            "provider": "Andrej Karpathy",
            "url": "https://www.youtube.com/watch?v=zjkBMFhNj_g",
            "type": "video",
            "trust_score": 10.0,
            "educational_quality": "Excellent",
            "difficulty": "Beginner",
            "estimated_duration": "1 hr",
            "provider_type": "Community"
        },
        {
            "title": "Transformers, the tech behind LLMs",
            "provider": "3Blue1Brown",
            "url": "https://www.youtube.com/watch?v=wjZofJX0v4M",
            "type": "video",
            "trust_score": 10.0,
            "educational_quality": "Excellent",
            "difficulty": "Intermediate",
            "estimated_duration": "30 min",
            "provider_type": "Community"
        }
    ],
    "opencv": [
        {
            "title": "OpenCV Course - Full Tutorial with Python",
            "provider": "freeCodeCamp",
            "url": "https://www.youtube.com/watch?v=oXlwWbU8_Z0",
            "type": "video",
            "trust_score": 9.8,
            "educational_quality": "Excellent",
            "difficulty": "Beginner",
            "estimated_duration": "3 hrs",
            "provider_type": "Community"
        }
    ],
    "spark": [
        {
            "title": "PySpark Tutorial for Beginners",
            "provider": "freeCodeCamp",
            "url": "https://www.youtube.com/watch?v=_C8kWso4ne4",
            "type": "video",
            "trust_score": 9.7,
            "educational_quality": "Excellent",
            "difficulty": "Beginner",
            "estimated_duration": "2 hrs",
            "provider_type": "Community"
        }
    ],
    "linux": [
        {
            "title": "Linux Command Line Full Course",
            "provider": "freeCodeCamp",
            "url": "https://www.youtube.com/watch?v=w-7RQ46RgxU",
            "type": "video",
            "trust_score": 9.8,
            "educational_quality": "Excellent",
            "difficulty": "Beginner",
            "estimated_duration": "4 hrs",
            "provider_type": "Community"
        }
    ]
}

def load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_resource_category(title, url):
    title_lower = title.lower()
    url_lower = url.lower()
    
    if "python" in title_lower:
        return "python"
    elif "sql" in title_lower or "postgres" in title_lower or "database" in title_lower:
        return "sql"
    elif "docker" in title_lower or "container" in title_lower:
        return "docker"
    elif "git" in title_lower or "github" in title_lower:
        return "git"
    elif "llm" in title_lower or "large language" in title_lower or "transformer" in title_lower or "attention" in title_lower:
        return "llm"
    elif "opencv" in title_lower or "vision" in title_lower:
        return "opencv"
    elif "spark" in title_lower or "pyspark" in title_lower:
        return "spark"
    elif "linux" in title_lower or "bash" in title_lower or "unix" in title_lower:
        return "linux"
    return "general"

def verify_and_get_resource(resource, week_goal="", week_objectives=[]):
    """
    Checks the status of a resource. If working, returns it.
    If broken, automatically replaces it with a working fallback or emergency AI resource.
    """
    url = resource.get("url", "")
    title = resource.get("title", "Learning Resource")
    provider = resource.get("provider", "Unknown")
    
    # Ingest default values for curation metadata if missing
    if "trust_score" not in resource:
        resource["trust_score"] = resource.get("trust_score", 9.5 if provider.lower() in ["mit", "harvard", "stanford"] else 8.5)
    if "educational_quality" not in resource:
        resource["educational_quality"] = "Excellent" if resource["trust_score"] >= 9.0 else "Good"
    if "difficulty" not in resource:
        resource["difficulty"] = "Beginner"
    if "estimated_duration" not in resource:
        resource["estimated_duration"] = "45 min"
    if "provider_type" not in resource:
        resource["provider_type"] = get_provider_type(provider, url)
    if "version" not in resource:
        resource["version"] = "v1"

    status_cache = load_json(STATUS_FILE)
    cached_info = status_cache.get(url, {})
    
    status = cached_info.get("status", "Working") # Default to working if not checked yet
    
    # Force known dead/placeholder YouTube IDs to be marked as Broken
    known_dead_ids = [
        "aircAruvnKk", "kqtD5eraMx8", "hG7hV-17xUM", "GZvSYJDk-Us", 
        "LlvBzyy-558", "X48VuDVv0do", "c9Wg6RyOx0U", "5sLYAJKMV-I", 
        "SOTamWGuqXs"
    ]
    if any(dead_id in url for dead_id in known_dead_ids):
        status = "Broken"
        
    if status == "Working":
        return resource

    # Resource is broken! Let's swap it with a fallback
    category = get_resource_category(title, url)
    fallbacks = FALLBACK_REGISTRY.get(category, [])
    
    # Try pre-defined fallbacks
    for fb in fallbacks:
        fb_url = fb["url"]
        fb_status = status_cache.get(fb_url, {}).get("status", "Working")
        if fb_status == "Working":
            updated = fb.copy()
            updated["version"] = "v2"
            updated["is_fallback"] = True
            updated["original_title"] = title
            updated["change_log"] = f"Original lecture became unavailable. Replaced with equivalent verified resource from {fb['provider']}."
            return updated
            
    # Try finding an alternative from resources.json
    res_db = load_json(RESOURCES_FILE)
    db_category_name = None
    for k in res_db.keys():
        if category in k.lower():
            db_category_name = k
            break
            
    if db_category_name:
        for db_res in res_db[db_category_name]:
            db_url = db_res.get("url", "")
            if db_url != url:
                db_status = status_cache.get(db_url, {}).get("status", "Working")
                if db_status == "Working":
                    updated = db_res.copy()
                    updated["version"] = "v2"
                    updated["is_fallback"] = True
                    updated["original_title"] = title
                    updated["change_log"] = f"Original resource became unavailable. Replaced with alternative from {db_res.get('provider')}."
                    return updated

    # All fallbacks failed! Call AI Emergency Recommendation
    ai_res = generate_emergency_resource(
        topic=category.capitalize(),
        goal=week_goal,
        objectives=week_objectives,
        difficulty=resource.get("difficulty", "Beginner"),
        duration=resource.get("estimated_duration", "45 min")
    )
    
    # Log emergency suggestion in status cache so we don't query LLM next time
    ai_res["version"] = "v2"
    ai_res["is_emergency"] = True
    ai_res["original_title"] = title
    ai_res["change_log"] = f"All fallbacks failed. Automatically generated equivalent emergency replacement from {ai_res.get('provider')}."
    
    # Pre-cache the emergency resource status as working
    status_cache[ai_res["url"]] = {
        "status": "Working",
        "last_checked": datetime.utcnow().strftime("%d %B %Y"),
        "trust_score": ai_res["trust_score"],
        "provider_type": ai_res["provider_type"]
    }
    # Mark the broken link in status file so we remember
    status_cache[url] = {
        "status": "Broken",
        "last_checked": datetime.utcnow().strftime("%d %B %Y"),
        "replacement_url": ai_res["url"]
    }
    save_json(STATUS_FILE, status_cache)
    
    return ai_res

def get_provider_type(provider, url):
    p_low = provider.lower()
    u_low = url.lower()
    
    if any(uni in p_low or uni in u_low for uni in ["mit", "stanford", "harvard", "berkeley", "ocw", "edu"]):
        return "University"
    elif any(d in p_low or d in u_low for d in ["docs", "tutorial", "reference", "python.org", "postgres", "react.dev", "docker.com"]):
        return "Official Docs"
    elif any(ind in p_low or ind in u_low for ind in ["google", "microsoft", "aws", "openai", "deeplearning", "figma"]):
        return "Industry"
    return "Community"
