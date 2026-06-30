import json
import os
import urllib.parse

ROLES_FILE = "database/roles.json"
CURRICULUM_FILE = "database/curriculum.json"

high_trust = [
    "stanford.edu", "mit.edu", "harvard.edu", "berkeley.edu", "cmu.edu",
    "python.org", "docker.com", "pytorch.org", "tensorflow.org", "kubernetes.io",
    "github.com", "microsoft.com", "google.com", "aws.amazon.com", "redhat.com",
    "owasp.org", "cncf.io", "linuxfoundation.org", "deeplearning.ai", "nvidia.com",
    "openai.com", "huggingface.co", "freecodecamp.org"
]
medium_trust = ["youtube.com", "youtu.be", "coursera.org", "udemy.com", "medium.com", "dev.to"]

def add_confidence_globally():
    if not os.path.exists(ROLES_FILE):
        print(f"[ERROR]: {ROLES_FILE} not found.")
        return
        
    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        roles_db = json.load(f)
        
    count = 0
    for role_name, role_data in roles_db.items():
        weeks = role_data.get("weekly_learning_sequence", [])
        for wk in weeks:
            resources = wk.get("resources", [])
            for res in resources:
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
                count += 1
                
    with open(ROLES_FILE, "w", encoding="utf-8") as f:
        json.dump(roles_db, f, indent=2)
    print(f"[SUCCESS]: Added confidence scores to {count} resources across roles.json.")

    curr_count = 0
    if os.path.exists(CURRICULUM_FILE):
        with open(CURRICULUM_FILE, "r", encoding="utf-8") as f:
            curr_db = json.load(f)
        for item in curr_db:
            weeks = item.get("weeks", [])
            for wk in weeks:
                resources = wk.get("resources", [])
                for res in resources:
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
                    curr_count += 1
        with open(CURRICULUM_FILE, "w", encoding="utf-8") as f:
            json.dump(curr_db, f, indent=2)
        print(f"[SUCCESS]: Added confidence scores to {curr_count} resources across curriculum.json.")

if __name__ == "__main__":
    add_confidence_globally()
