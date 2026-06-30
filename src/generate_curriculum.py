import os
import sys
import json
import time
import asyncio
from dotenv import load_dotenv

sys.path.append("d:\\skillbridge-ai")

from google.adk.runners import InMemoryRunner
from src.agents_config import curriculum_designer_agent
from google.genai import types

load_dotenv()

ROLE_TEMPLATES = {
    "Artificial Intelligence": [
        "AI Specialist", "AI Researcher", "Cognitive Systems Architect",
        "AI Solutions Engineer", "AI Strategy Consultant", "AI Ethicist",
        "Applied AI Engineer", "Autonomous Systems Specialist"
    ],
    "Agentic AI": [
        "Agentic AI Developer", "AI Workflow Engineer", "AI Automation Engineer",
        "Multi-Agent Systems Engineer", "AI Integration Engineer", "Enterprise Agent Developer",
        "RPA AI Specialist", "Cognitive Flow Architect"
    ],
    "Machine Learning": [
        "Machine Learning Engineer", "Applied ML Engineer", "Feature Store Specialist",
        "ML Research Scientist", "ML Pipeline Developer", "Model Optimization Engineer",
        "ML Platform Engineer", "MLOps Automation Lead"
    ],
    "Deep Learning": [
        "Deep Learning Engineer", "Neural Networks Specialist", "GPU Tuning Engineer",
        "DL Research Scientist", "Vision DL Architect", "Transformer Engineer",
        "Compute Resource Allocator", "Quantization Specialist"
    ],
    "Large Language Models": [
        "LLM Developer", "LLM Evaluation Specialist", "Prompt Engineer",
        "RAG Engineer", "Vector Database Specialist", "LLM Security Auditor",
        "Fine-Tuning Specialist", "Context Optimization Engineer"
    ],
    "Natural Language Processing": [
        "NLP Engineer", "Conversational AI Designer", "Semantic Search Specialist",
        "Computational Linguist", "NLP Researcher", "Text Analytics Engineer",
        "Speech Processing Engineer", "NLP Database Admin"
    ],
    "Computer Vision": [
        "Computer Vision Engineer", "Image Processing Specialist", "Perception Engineer",
        "Visual CV Architect", "Spatial Processing Developer", "CV Optimization Engineer",
        "Video Analytics Developer", "CV Quality Analyst"
    ],
    "Data Science": [
        "Data Scientist", "Decision Scientist", "Quantitative Analyst",
        "Applied Statistician", "Data Modeler", "Data Science Lead",
        "Predictive Modeler", "Experimental Designer"
    ],
    "Data Analytics": [
        "Data Analyst", "Business Intelligence Analyst", "Product Data Analyst",
        "Excel Specialist", "BI Developer", "Marketing Analyst",
        "Sales Data Consultant", "Operations Analyst"
    ],
    "Data Engineering": [
        "Data Pipeline Engineer", "Database Engineer", "Data Warehouse Architect",
        "ETL Developer", "Postgres Administrator", "Data Lake Specialist",
        "Spark Operations Lead", "DB Integration Engineer"
    ],
    "Software Engineering": [
        "Backend Developer", "Frontend Developer", "Full Stack Developer",
        "Software Engineer", "Systems Engineer", "Application Developer",
        "Git Operations Lead", "Desktop App Engineer"
    ],
    "Backend Development": [
        "Backend Engineer", "API Developer", "Serverless Specialist",
        "FastAPI Developer", "REST API Architect", "Database Connections Lead",
        "Backend Security Architect", "Python Server Developer"
    ],
    "Frontend Development": [
        "Frontend Engineer", "UI Developer", "SPA Developer",
        "React Web Developer", "Web Designer", "Responsive Layout Builder",
        "CSS Architect", "Component Library Maintainer"
    ],
    "Full Stack Development": [
        "Full Stack Web Developer", "Full-Stack AI Developer", "Rapid Prototyping Engineer",
        "Web App Lead", "Deployments Architect", "Figma-to-Code Developer",
        "FullStack Security Specialist", "SaaS Developer"
    ],
    "Mobile Development": [
        "Mobile App Engineer", "iOS Developer", "Android Developer",
        "Flutter Developer", "React Native Developer", "Mobile UI Builder",
        "Mobile Security Analyst", "Mobile Performance Specialist"
    ],
    "Cloud Computing": [
        "Cloud Solutions Architect", "Cloud Systems Administrator", "Cloud Security Engineer",
        "AWS Architect", "Virtualization Specialist", "Cloud Scaling Lead",
        "Multicloud Coordinator", "Cloud FinOps Analyst"
    ],
    "DevOps": [
        "DevOps Engineer", "Platform Engineer", "Release Coordinator",
        "CI/CD Pipeline Lead", "Containerization Lead", "Docker Specialist",
        "DevOps Automation Engineer", "Kubernetes Deployment Lead"
    ],
    "Site Reliability Engineering": [
        "Site Reliability Engineer", "SRE Lead", "Infrastructure Automation Engineer",
        "Systems Reliability Auditor", "Chaos Engineering Lead", "Monitoring Analyst",
        "Infrastructure Developer", "Network Reliability Architect"
    ],
    "Cybersecurity": [
        "SOC Analyst", "Penetration Tester", "Cybersecurity Engineer",
        "Security Auditor", "Threat Intelligence Analyst", "Network Defender",
        "Incident Response Specialist", "Vulnerability Auditor"
    ],
    "UI/UX Design": [
        "UI/UX Designer", "Product Designer", "Interaction Designer",
        "Figma Prototyper", "UX Researcher", "Usability Analyst",
        "Wireframe Architect", "Visual Design Specialist"
    ]
}

os.makedirs("database", exist_ok=True)
ROLES_FILE = "database/roles.json"
if os.path.exists(ROLES_FILE):
    try:
        with open(ROLES_FILE, "r", encoding="utf-8") as f:
            roles_db = json.load(f)
    except Exception:
        roles_db = {}
else:
    roles_db = {}

runner = InMemoryRunner(agent=curriculum_designer_agent, app_name="curriculum_builder")

async def generate_role_curriculum(domain_name, role_name):
    print(f"Generating curriculum for: {role_name} (Domain: {domain_name})...")
    
    prompt = f"""
    You are an expert university curriculum designer, senior industry mentor, and technical editor. 
    Generate a 10/10 competency-first, video-first learning path curriculum for the following role:
    Role: {role_name}
    Domain: {domain_name}

    Follow these strict curriculum design instructions (Version 4.0 Quality Framework):
    1. Focus on job readiness and employability. Answer: "What knowledge, skills and practical experience must someone acquire to become employable in this role?" rather than generic topic coverage.
    2. Dependency Graph Ordering: Order weeks according to prerequisite relationships. The learner should never encounter a concept before learning its prerequisites.
    3. Competency Graph Boundaries: Include only Core Competencies in the main roadmap weeks. Exclude unnecessary adjacent technologies.
    4. The curriculum must be video-first. Mappings must use the highest quality educational providers.
    Priority Order:
    - Tier 1: DeepLearning.AI, Stanford, MIT OpenCourseWare, Harvard CS50, CMU, Microsoft Learn, Google Cloud Skills Boost, NVIDIA DLI, IBM SkillsBuild, Hugging Face, OpenAI, Anthropic, and Official canonical product documentation (e.g., docs.docker.com, pytorch.org).
    - Tier 2: freeCodeCamp, Fireship, official conference talks, university lecture series, high-quality technical YouTube playlists.
    - Tier 3: Independent creators only when clearly superior. Avoid generic tutorials.
    5. Every week must contain:
       - 1 flagship learning resource (e.g. video course, playlist, or university lecture)
       - 1 supplementary resource (video or article)
       - 1 documentation reference (if useful)
       - 1 hands-on practice lab
    6. Every week must have a clear Weekly Goal, specific Learning Objectives (2-4 items), 2-4 Resources, a Hands-on Practice lab task, a Mini Project, Expected Skills Gained, a specific GitHub Portfolio Artifact produced, and a Checkpoint Question.
    7. Avoid generic week titles (e.g., "Master {role_name} details"). Use meaningful, specific titles representing the learning outcomes (e.g., "Understanding Prompt Design and LLM Interaction").

    Respond strictly with a valid JSON object (no markdown formatting, no code block backticks, just raw JSON) matching this schema:
    {{
      "role_overview": "A detailed 2-3 sentence overview of this role's purpose from an industry perspective.",
      "daily_responsibilities": [
        "Specific daily responsibility 1",
        "Specific daily responsibility 2",
        "Specific daily responsibility 3"
      ],
      "industry_expectations": "What the industry expects from a mid-level professional in this role.",
      "core_competencies": [
        "Core Competency 1 (Required)",
        "Core Competency 2 (Required)",
        "Core Competency 3 (Required)"
      ],
      "supporting_competencies": [
        "Supporting Competency 1 (Useful but optional)",
        "Supporting Competency 2 (Useful but optional)"
      ],
      "technologies_used": [
        "Technology/Tool 1",
        "Technology/Tool 2"
      ],
      "learning_objectives": [
        "Primary learning objective 1",
        "Primary learning objective 2"
      ],
      "recommended_projects": [
        "Portfolio Project 1",
        "Portfolio Project 2"
      ],
      "weekly_learning_sequence": [
        {{
          "week": 1,
          "goal": "Specific goal/title representing outcome",
          "objectives": [
            "Objective 1",
            "Objective 2"
          ],
          "resources": [
            {{
              "title": "Title of course or video",
              "provider": "e.g. DeepLearning.AI / YouTube / Stanford",
              "url": "https://...",
              "type": "video"
            }}
          ],
          "practice": "Detailed hands-on lab or exercise description",
          "project": "Mini project description supporting the week's goals",
          "expected_skills_gained": "Specific skills acquired this week",
          "github_portfolio_artifact": "Specific file or repository artifact committed to their GitHub portfolio for this week",
          "checkpoint": "Self-assessment checkpoint question"
        }}
      ]
    }}
    """
    
    loop_session = await runner.session_service.create_session(app_name="curriculum_builder", user_id="MARIUM_TARIQ")
    msg = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    response = ""
    async for event in runner.run_async(user_id="MARIUM_TARIQ", session_id=loop_session.id, new_message=msg) or []:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response += part.text
                    
    cleaned_res = response.strip()
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
        
    data = json.loads(cleaned_res)
    return data

async def main():
    total_processed = 0
    
    # Load multiple Gemini API Keys for rotation
    gemini_keys_str = os.environ.get("GEMINI_API_KEYS", "")
    GEMINI_KEYS = [k.strip() for k in gemini_keys_str.split(",") if k.strip()]
    current_key_idx = 0
    
    for domain_name, roles_list in ROLE_TEMPLATES.items():
        for role_name in roles_list:
            # Skip if already exists with full Version 4.0 fields
            if role_name in roles_db:
                obj = roles_db[role_name]
                if all(k in obj for k in ["role_overview", "daily_responsibilities", "weekly_learning_sequence"]) and len(obj.get("weekly_learning_sequence", [])) >= 4:
                    first_wk = obj.get("weekly_learning_sequence", [])[0]
                    if "github_portfolio_artifact" in first_wk:
                        print(f"Skipping {role_name} (already fully populated under Version 4.0).")
                        continue
            
            retries = 10
            while retries > 0:
                try:
                    data = await generate_role_curriculum(domain_name, role_name)
                    
                    roles_db[role_name] = {
                        "domain": domain_name,
                        "role_overview": data.get("role_overview", ""),
                        "daily_responsibilities": data.get("daily_responsibilities", []),
                        "industry_expectations": data.get("industry_expectations", ""),
                        "core_competencies": data.get("core_competencies", []),
                        "supporting_competencies": data.get("supporting_competencies", []),
                        "technologies_used": data.get("technologies_used", []),
                        "learning_objectives": data.get("learning_objectives", []),
                        "recommended_projects": data.get("recommended_projects", []),
                        "weekly_learning_sequence": data.get("weekly_learning_sequence", []),
                        "curated_resources": [res for wk in data.get("weekly_learning_sequence", []) for res in wk.get("resources", [])]
                    }
                    
                    with open(ROLES_FILE, "w", encoding="utf-8") as f:
                        json.dump(roles_db, f, indent=2)
                        
                    print(f"[SUCCESS] Saved curriculum for: {role_name}")
                    total_processed += 1
                    break
                except Exception as e:
                    retries -= 1
                    err_str = str(e)
                    is_rate_limit = any(term in err_str.lower() for term in ["rate limit", "429", "tpm", "quota", "resource_exhausted", "unavailable"])
                    
                    print(f"[ERROR] Failed generating for {role_name}: {e}. Retries left: {retries}")
                    
                    if is_rate_limit and GEMINI_KEYS:
                        current_key_idx = (current_key_idx + 1) % len(GEMINI_KEYS)
                        next_key = GEMINI_KEYS[current_key_idx]
                        print(f"[System Alert]: Key limit hit. Rotating to next Gemini key: {next_key[:10]}...")
                        
                        from google.genai import Client
                        # Rotate key dynamically on the LlmAgent model
                        curriculum_designer_agent.model.api_client = Client(api_key=next_key)
                        
                        await asyncio.sleep(2)
                        continue
                    
                    # Sleep longer on other rate limits
                    wait_time = 25 if is_rate_limit else 8
                    print(f"Waiting for {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
                    
                    if retries == 0:
                        print(f"[CRITICAL] Skipping {role_name} after 10 failures.")
            
            # Safe Cool-down interval between successful calls
            sleep_time = 4.5 if os.environ.get("GEMINI_API_KEY") else 12
            await asyncio.sleep(sleep_time)
            
    # Compile curriculum.json backup
    curriculum_list = []
    for r_name, r_data in roles_db.items():
        if "weekly_learning_sequence" in r_data:
            curriculum_list.append({
                "role": r_name,
                "weeks": r_data["weekly_learning_sequence"]
            })
            
    with open("database/curriculum.json", "w", encoding="utf-8") as f:
        json.dump(curriculum_list, f, indent=2)
        
    print(f"\n[DONE] Finished processing. Total new roadmaps generated: {total_processed}")

if __name__ == "__main__":
    asyncio.run(main())
