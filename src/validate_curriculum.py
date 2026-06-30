import json
import os

ROLES_FILE = "database/roles.json"

FLAGSHIP_ROLES = [
    "Penetration Tester",
    "Machine Learning Engineer",
    "Cloud Solutions Architect",
    "Full Stack Developer",
    "Data Scientist",
    "DevOps Engineer",
    "Data Pipeline Engineer",
    "Frontend Engineer",
    "Backend Engineer",
    "UI/UX Designer"
]

def validate_roles(roles_file=ROLES_FILE):
    if not os.path.exists(roles_file):
        print(f"[ERROR]: {roles_file} does not exist.")
        return False
        
    with open(roles_file, "r", encoding="utf-8") as f:
        try:
            roles_db = json.load(f)
        except Exception as e:
            print(f"[ERROR]: Failed to load {roles_file}: {e}")
            return False
            
    print(f"Loaded {len(roles_db)} roles for validation...")
    
    missing_fields_flagship = []
    missing_fields_week = []
    invalid_confidence = []
    duplicate_resources = []
    
    for role_name, role_data in roles_db.items():
        if role_name in FLAGSHIP_ROLES:
            # Strictly validate V6 Flagship properties
            required_v6_fields = [
                "role_difficulty_tier", "estimated_learning_hours",
                "exit_outcomes", "specialization_branches", "standardized_capstone",
                "weekly_learning_sequence"
            ]
            missing = [f for f in required_v6_fields if f not in role_data]
            if missing:
                missing_fields_flagship.append((role_name, missing))
                
            weeks = role_data.get("weekly_learning_sequence", [])
            if not weeks:
                missing_fields_flagship.append((role_name, ["non-empty weekly_learning_sequence"]))
                
            urls_seen = set()
            for wk in weeks:
                week_num = wk.get("week", 0)
                
                # Check V6 weekly fields
                required_week = [
                    "why_this_week_exists", "weekly_time_breakdown",
                    "practice", "project", "evolving_repository_name", "checkpoint_v6"
                ]
                missing_wk = [f for f in required_week if f not in wk]
                if missing_wk:
                    missing_fields_week.append((role_name, week_num, missing_wk))
                    
                # Check resource confidence ratings
                resources = wk.get("resources", [])
                for res in resources:
                    url = res.get("url")
                    if url:
                        if url in urls_seen:
                            duplicate_resources.append((role_name, week_num, url))
                        urls_seen.add(url)
                    
                    confidence = res.get("confidence")
                    if confidence not in ["High", "Medium", "Needs Review"]:
                        invalid_confidence.append((role_name, week_num, res.get("title"), confidence))
                        
    # Print report
    print("\n=== strict V6 Flagship Validation Report ===")
    print(f"Flagship roles missing key V6 fields count: {len(missing_fields_flagship)}")
    if missing_fields_flagship:
        for r, f in missing_fields_flagship:
            print(f" - Flagship Role '{r}' missing: {f}")
            
    print(f"Flagship weeks missing V6 metadata count: {len(missing_fields_week)}")
    if missing_fields_week:
        for r, w, f in missing_fields_week[:10]:
            print(f" - Flagship Role '{r}', Week {w} missing: {f}")
            
    print(f"Resources missing/invalid confidence ratings count: {len(invalid_confidence)}")
    if invalid_confidence:
        for r, w, t, c in invalid_confidence[:10]:
            print(f" - Flagship Role '{r}', Week {w}, Resource '{t}' has confidence: {c}")
            
    print(f"Duplicate resource URLs count: {len(duplicate_resources)}")
    if duplicate_resources:
        for r, w, url in duplicate_resources[:5]:
            print(f" - Role '{r}', Week {w} repeats URL: {url}")
            
    success = (len(missing_fields_flagship) == 0 and 
               len(missing_fields_week) == 0 and 
               len(invalid_confidence) == 0)
    return success

if __name__ == "__main__":
    success = validate_roles()
    if success:
        print("\n[SUCCESS]: All strict V6 validation checks passed for flagship roles!")
    else:
        print("\n[ERROR]: Some V6 validation checks failed. See details above.")
