import os
import json
import asyncio
import httpx
from datetime import datetime
try:
    from src.resource_validator import get_provider_type, get_resource_category
except ModuleNotFoundError:
    from resource_validator import get_provider_type, get_resource_category

CURRICULUM_FILE = "database/curriculum.json"
RESOURCES_FILE = "database/resources.json"
STATUS_FILE = "database/resource_status.json"
REPORT_FILE = "C:/Users/LENOVO/.gemini/antigravity/brain/67f54746-cb5c-48df-b141-fdb667672728/admin_resource_report.md"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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

def extract_all_resources():
    urls = {} # url -> dict (title, provider, type)
    
    # 1. From Curriculum
    curr = load_json(CURRICULUM_FILE)
    if isinstance(curr, list):
        for role_data in curr:
            weeks = role_data.get("weeks", [])
            for w in weeks:
                res_list = w.get("resources", [])
                for res in res_list:
                    url = res.get("url", "")
                    if url:
                        urls[url] = {
                            "title": res.get("title", ""),
                            "provider": res.get("provider", ""),
                            "type": res.get("type", "video")
                        }
                        
    # 2. From Resources
    res_db = load_json(RESOURCES_FILE)
    if isinstance(res_db, dict):
        for cat, items in res_db.items():
            if isinstance(items, list):
                for res in items:
                    if isinstance(res, dict):
                        url = res.get("url", "")
                        if url:
                            urls[url] = {
                                "title": res.get("title", ""),
                                "provider": res.get("provider", ""),
                                "type": res.get("type", "video")
                            }
            elif isinstance(items, dict):
                url = cat
                if url.startswith("http"):
                    urls[url] = {
                        "title": items.get("title", ""),
                        "provider": items.get("provider", ""),
                        "type": items.get("type", "video")
                    }
                    
    return urls

async def verify_url(client, url, info):
    title = info["title"]
    p_type = get_provider_type(info["provider"], url)
    category = get_resource_category(title, url)
    
    # Default fallback values for trust scores
    t_score = 9.5 if p_type == "University" else (9.0 if p_type == "Official Docs" else 8.5)
    
    result = {
        "url": url,
        "title": title,
        "provider": info["provider"],
        "provider_type": p_type,
        "trust_score": t_score,
        "last_checked": datetime.utcnow().strftime("%d %B %Y"),
        "status": "Working"
    }

    try:
        if "youtube.com" in url or "youtu.be" in url:
            # YouTube verification via watch page GET request
            res = await client.get(url, headers=HEADERS, timeout=8.0)
            if res.status_code == 200:
                html = res.text
                if any(term in html for term in ["Video unavailable", "This video is unavailable", "This video is no longer available", "videoIsUnavailable"]):
                    result["status"] = "Broken"
                    result["reason"] = "YouTube: Video unavailable / deleted"
                else:
                    result["status"] = "Working"
            else:
                result["status"] = "Broken"
                result["reason"] = f"YouTube response: HTTP {res.status_code}"
        else:
            # General link verification
            res = await client.get(url, headers=HEADERS, timeout=8.0, follow_redirects=True)
            if res.status_code in [200, 301, 302]:
                result["status"] = "Working"
            elif res.status_code in [403, 401]:
                # Many official documentation pages block scrapers, we treat them as working
                # if the domain resolves, but log it
                result["status"] = "Working"
                result["reason"] = f"HTTP {res.status_code} (Bypassed scraper block)"
            else:
                result["status"] = "Broken"
                result["reason"] = f"HTTP {res.status_code}"
    except httpx.TimeoutException:
        result["status"] = "Broken"
        result["reason"] = "Connection Timeout"
    except Exception as e:
        result["status"] = "Broken"
        result["reason"] = f"Connection Error: {str(e)}"
        
    return result

async def check_all_resources_async(dev_mode=True):
    resources = extract_all_resources()
    print(f"Loaded {len(resources)} unique resources to check.")
    
    status_cache = load_json(STATUS_FILE)
    
    sem = asyncio.Semaphore(30)
    
    async def sem_verify(client, url, info):
        async with sem:
            return await verify_url(client, url, info)
            
    async with httpx.AsyncClient(verify=False) as client:
        tasks = []
        for url, info in resources.items():
            # If in production mode, skip URLs checked in the last 24 hours
            if not dev_mode and url in status_cache:
                last_checked_str = status_cache[url].get("last_checked", "")
                try:
                    last_checked_date = datetime.strptime(last_checked_str, "%d %B %Y")
                    delta = datetime.utcnow() - last_checked_date
                    if delta.days < 1:
                        continue
                except Exception:
                    pass
            tasks.append(sem_verify(client, url, info))
            
        print(f"Verifying {len(tasks)} resources with concurrency limit 30...")
        results = await asyncio.gather(*tasks)
        
        for res in results:
            url = res["url"]
            # Preserve replacement history and versioning if already present
            existing = status_cache.get(url, {})
            status_cache[url] = {
                "status": res["status"],
                "last_checked": res["last_checked"],
                "trust_score": existing.get("trust_score", res["trust_score"]),
                "provider_type": existing.get("provider_type", res["provider_type"]),
                "version": existing.get("version", "v1"),
                "reason": res.get("reason", "")
            }
            if "replacement_url" in existing:
                status_cache[url]["replacement_url"] = existing["replacement_url"]
            if "change_history" in existing:
                status_cache[url]["change_history"] = existing["change_history"]
                
        save_json(STATUS_FILE, status_cache)
        print(f"[SUCCESS] Resource verification cache updated at {STATUS_FILE}.")
        
        # Compile statistics & Admin Report
        generate_admin_report(status_cache)

def get_health_stats(status_cache=None):
    if status_cache is None:
        status_cache = load_json(STATUS_FILE)
        
    total = len(status_cache)
    if total == 0:
        return {}
        
    working = sum(1 for v in status_cache.values() if v.get("status") == "Working")
    broken = sum(1 for v in status_cache.values() if v.get("status") == "Broken")
    replaced = sum(1 for v in status_cache.values() if "replacement_url" in v or v.get("version", "v1") != "v1")
    pending = sum(1 for v in status_cache.values() if v.get("status") == "Pending")
    
    total_trust = sum(v.get("trust_score", 8.5) for v in status_cache.values())
    avg_trust = total_trust / total if total > 0 else 0.0
    
    # Provider types
    unis = sum(1 for v in status_cache.values() if v.get("provider_type") == "University")
    docs = sum(1 for v in status_cache.values() if v.get("provider_type") == "Official Docs")
    inds = sum(1 for v in status_cache.values() if v.get("provider_type") == "Industry")
    comm = sum(1 for v in status_cache.values() if v.get("provider_type") == "Community")
    
    return {
        "total": total,
        "working": working,
        "broken": broken,
        "replaced": replaced,
        "pending": pending,
        "avg_trust": avg_trust,
        "percentages": {
            "University": int((unis / total) * 100) if total > 0 else 0,
            "Official Docs": int((docs / total) * 100) if total > 0 else 0,
            "Industry": int((inds / total) * 100) if total > 0 else 0,
            "Community": int((comm / total) * 100) if total > 0 else 0
        }
    }

def generate_admin_report(status_cache):
    stats = get_health_stats(status_cache)
    if not stats:
        return
        
    broken_list = []
    replaced_list = []
    
    for url, v in status_cache.items():
        if v.get("status") == "Broken":
            broken_list.append(f"- **URL**: {url}  \n  *Reason*: {v.get('reason', 'N/A')} | *Last Checked*: {v.get('last_checked')}")
        if "replacement_url" in v:
            replaced_list.append(f"- **Original URL**: {url}  \n  *Replaced with*: {v.get('replacement_url')}  \n  *Last Checked*: {v.get('last_checked')}")
            
    report_md = f"""# Admin Resource Health & Curation Report

Generated on: {datetime.utcnow().strftime("%d %B %Y %H:%M UTC")}

## Overall Platform Health Stats

| Metric | Value |
| :--- | :--- |
| **Total Resources** | {stats['total']} |
| **Verified & Working** | {stats['working']} |
| **Broken & Flagged** | {stats['broken']} |
| **Auto Replaced** | {stats['replaced']} |
| **Average Trust Score** | {stats['avg_trust']:.2f} / 10.0 |

### Source Distribution

- 🎓 **University Sources**: {stats['percentages']['University']}%
- 🏛 **Official Docs**: {stats['percentages']['Official Docs']}%
- 💼 **Industry Providers**: {stats['percentages']['Industry']}%
- 👥 **Community Resources**: {stats['percentages']['Community']}%

---

## Flagged Broken Links ({len(broken_list)})

{chr(10).join(broken_list) if broken_list else "No broken links flagged."}

---

## Auto-Replaced Link History ({len(replaced_list)})

{chr(10).join(replaced_list) if replaced_list else "No link replacements recorded."}
"""

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"[SUCCESS] Admin report created at {REPORT_FILE}.")

if __name__ == "__main__":
    # Default to dev mode checking all links
    asyncio.run(check_all_resources_async(dev_mode=True))
