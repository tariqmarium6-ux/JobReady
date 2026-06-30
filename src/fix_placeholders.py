import os
import json

STATUS_FILE = "database/resource_status.json"

def main():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            status_cache = json.load(f)
    else:
        status_cache = {}

    # Pre-seed the broken placeholder links
    status_cache["https://www.youtube.com/watch?v=kqtD5eraMx8"] = {
        "status": "Broken",
        "last_checked": "28 June 2026",
        "trust_score": 5.0,
        "provider_type": "Community",
        "reason": "YouTube: Video unavailable / deleted"
    }

    status_cache["https://www.youtube.com/watch?v=5sLYAJKMV-I"] = {
        "status": "Broken",
        "last_checked": "28 June 2026",
        "trust_score": 4.0,
        "provider_type": "Community",
        "reason": "Incorrect placeholder (C+C Music Factory music video)"
    }

    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status_cache, f, indent=2)

    print("[SUCCESS] Pre-seeded broken placeholder statuses in status file.")

if __name__ == "__main__":
    main()
