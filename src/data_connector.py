import os
import requests
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

# High-fidelity simulated real-world job demand keywords for the 12 target AI roles
# Act as a bulletproof fallback if API keys are missing, network is down, or limits are hit.
FALLBACK_JOBS = {
    "AI Product Support": [
        {
            "title": "AI Technical Support Specialist",
            "company": "CognitiveLabs",
            "description": "Looking for an AI Support Specialist to troubleshoot prompt interfaces, support API integrations, and explain LLM behavior to users. Required: Prompt Engineering, API Fundamentals, Customer Support, Basic Troubleshooting."
        },
        {
            "title": "LLM Product Support Associate",
            "company": "Agentic AI",
            "description": "Help clients integrate our model endpoints. Troubleshoot prompt pipelines and monitor API requests. Required: Prompt Engineering, API Fundamentals, Customer Support."
        }
    ],
    "LLM Evaluation Specialist": [
        {
            "title": "LLM Evaluation and Quality Analyst",
            "company": "Decenter AI",
            "description": "Evaluate model outputs for accuracy, safety, and toxicity. Build test datasets and define evaluation metrics. Required: Prompt Engineering, LLM Fundamentals, Model Evaluation Metrics, Data Labeling."
        },
        {
            "title": "AI Model Tester (LLM Evaluator)",
            "company": "Helix Systems",
            "description": "Help audit our generative models. Create testing prompts, perform toxicity and bias analysis, and label outputs. Required: Prompt Engineering, LLM Fundamentals, Model Evaluation Metrics, Data Labeling."
        }
    ],
    "RAG Architect": [
        {
            "title": "Senior RAG Architect",
            "company": "VectorFlow",
            "description": "Design semantic search pipelines, optimize index strategies, and build low-latency RAG architectures using vector databases. Required: Python, Vector Databases, Embeddings, LLM Orchestration, Semantic Search."
        },
        {
            "title": "AI Retrieval & RAG Engineer",
            "company": "SearchGen",
            "description": "Build agentic search retrieval pipelines. Combine document embeddings with vector databases for Q&A agents. Required: Python, Vector Databases, Embeddings, LLM Orchestration, Semantic Search."
        }
    ],
    "Data Quality Analyst": [
        {
            "title": "AI Data Quality Analyst",
            "company": "CleanData Corp",
            "description": "Verify incoming datasets for AI training. Run SQL audits, perform data cleaning, and maintain data pipeline integrity. Required: SQL Basics, Data Auditing, Excel Advanced, Data Cleaning."
        },
        {
            "title": "Data Quality Auditor",
            "company": "SmartData",
            "description": "Analyze and audit training datasets. Write SQL queries to find duplicates and clean records. Required: SQL Basics, Data Auditing, Excel Advanced, Data Cleaning."
        }
    ],
    "AI Data Pipeline Engineer": [
        {
            "title": "AI Data Pipeline Engineer",
            "company": "DataStream AI",
            "description": "Design and scale real-time ingestion pipelines. Work with Spark, SQL, and Vector Databases to feed downstream models. Required: Python, SQL Basics, Apache Spark, Vector Databases, Data Engineering."
        }
    ],
    "Vector DB Specialist": [
        {
            "title": "Vector Database Engineer",
            "company": "EmbedDB",
            "description": "Deploy, optimize, and scale index strategies for Qdrant and Pinecone vector stores. Required: Python, Vector Databases, Embeddings, Index Optimization, SQL Basics."
        }
    ],
    "AI Compliance Officer": [
        {
            "title": "AI Regulatory and Compliance Officer",
            "company": "Trustworthy AI",
            "description": "Ensure our LLM applications align with global regulatory frameworks (EU AI Act). Maintain audit logs and run risk assessments. Required: AI Ethics Basics, Regulatory Frameworks, Risk Assessment, Audit Logging."
        }
    ],
    "AI Alignment Auditor": [
        {
            "title": "AI Safety and Alignment Auditor",
            "company": "Guardrail Labs",
            "description": "Perform safety audits of generative models. Conduct red teaming exercises, align outputs using reinforcement learning, and calculate evaluation metrics. Required: AI Ethics Basics, Model Evaluation Metrics, Reinforcement Learning Basics, Red Teaming."
        }
    ],
    "Model Safety Evaluator": [
        {
            "title": "LLM Safety Evaluator",
            "company": "SafetyNet AI",
            "description": "Evaluate LLMs for toxicity, jailbreaks, and hallucinations. Configure guardrails and run adversarial red teaming. Required: Prompt Engineering, Red Teaming, LLM Guardrails, Toxicity Analysis."
        }
    ],
    "AI Operations Specialist": [
        {
            "title": "AI Operations Engineer (MLOps)",
            "company": "InferenceOps",
            "description": "Deploy and monitor LLMs in production. Setup Docker containers, track model performance, and troubleshoot hosted model endpoints. Required: Inference APIs, Model Deployment, Docker, Monitoring Tools."
        }
    ],
    "LLM Fine-Tuning Specialist": [
        {
            "title": "LLM Fine-Tuning Engineer",
            "company": "Weights & Fine-Tuning",
            "description": "Perform parameter-efficient fine-tuning (LoRA, QLoRA) on open models. Optimize GPU memory usage using PyTorch. Required: Python, PyTorch, PEFT Techniques, GPU Memory Management, LLM Fundamentals."
        }
    ],
    "Inference Scaling Specialist": [
        {
            "title": "Inference Infrastructure Specialist",
            "company": "vScale AI",
            "description": "Build high-throughput inference endpoints. Deploy vLLM engines and Triton servers on Kubernetes clusters. Required: Docker, Kubernetes, vLLM Engine, Triton Server, Inference APIs."
        }
    ]
}

def query_adzuna_jobs(keyword, country_code="us", max_results=5):
    """
    Queries the Adzuna job search API for live postings matching the keyword.
    Falls back to hand-curated real-world jobs if API keys are missing or requests fail.
    """
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("[!] Adzuna API credentials missing. Engaging high-fidelity fallback data...")
        return get_fallback_jobs(keyword)

    url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": keyword,
        "results_per_page": max_results,
        "content-type": "application/json"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get("results", [])
            if jobs:
                formatted_jobs = []
                for j in jobs:
                    formatted_jobs.append({
                        "title": j.get("title", ""),
                        "company": j.get("company", {}).get("display_name", ""),
                        "description": j.get("description", ""),
                        "location": j.get("location", {}).get("display_name", "")
                    })
                return formatted_jobs
            else:
                print(f"[!] No jobs returned from Adzuna for '{keyword}'. Using fallback...")
                return get_fallback_jobs(keyword)
        else:
            print(f"[!] Adzuna API returned status {response.status_code}. Using fallback...")
            return get_fallback_jobs(keyword)
    except Exception as e:
        print(f"[!] Exception calling Adzuna API: {e}. Using fallback...")
        return get_fallback_jobs(keyword)

def get_fallback_jobs(keyword):
    """
    Searches the hand-curated database for jobs matching the search query keywords.
    """
    results = []
    # Simple keyword matching against fallback database keys
    for role_name, jobs in FALLBACK_JOBS.items():
        if keyword.lower() in role_name.lower() or role_name.lower() in keyword.lower():
            results.extend(jobs)
    
    # If no direct match, return a general set of relevant AI-adjacent positions
    if not results:
        for jobs in FALLBACK_JOBS.values():
            results.extend(jobs)
            if len(results) >= 5:
                break
                
    return results[:5]
